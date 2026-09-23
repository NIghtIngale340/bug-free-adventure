"""
STATEFUL SIMULATION SERVICE (Step-by-Step)
Owner: Ken (Backend / Automata Core Lead)
Task: BE-006

Public contract (frozen — see SHARED_ARCHITECTURE_AND_CONTRACTS.md):
    create_session(input_string: str) -> str
    step(session_id: str) -> Optional[TransitionStep]
    run_all(session_id: str) -> SimulationResult
    reset(session_id: str) -> None
    get_metadata() -> AutomataMetadata

Used by: Chester's Page 2 (Step-by-Step Simulator) and Page 3 (Automata Explorer).
"""

import uuid
from dataclasses import dataclass, field

from app.core.dfa import DFA
from app.core.language import is_symbol_in_alphabet
from app.core.models import (
    AutomataMetadata,
    SimulationResult,
    SimulationStatus,
    TransitionStep,
)
from app.core.simulator import simulate
from app.data.id_rules import (
    ACCEPTING_STATES,
    ALPHABET,
    CANONICAL_STATES,
    CANONICAL_TRANSITIONS,
    RE_PATTERN,
    START_STATE,
    TRAP_STATE,
)


@dataclass
class _Session:
    """Internal, mutable state for one stepping session."""
    input_string: str
    state: str = START_STATE
    cursor: int = 0
    trace: list[TransitionStep] = field(default_factory=list)
    finished: bool = False
    rejected_reason: SimulationStatus | None = None


class SimulationService:
    """Stateful stepping facade over the Minimized DFA."""

    def __init__(self) -> None:
        self._dfa = DFA()
        self._sessions: dict[str, _Session] = {}

    # --- Session lifecycle ------------------------------------------------

    def create_session(self, input_string: str) -> str:
        session_id = uuid.uuid4().hex
        self._sessions[session_id] = _Session(input_string=input_string)
        return session_id

    def reset(self, session_id: str) -> None:
        session = self._sessions.get(session_id)
        if session is None:
            return
        session.state = START_STATE
        session.cursor = 0
        session.trace = []
        session.finished = False
        session.rejected_reason = None

    # --- Stepping ---------------------------------------------------------

    def step(self, session_id: str) -> TransitionStep | None:
        """
        Advance one symbol. Returns the TransitionStep, or None when the
        session has finished (accepted, rejected, or exhausted).
        """
        session = self._sessions.get(session_id)
        if session is None or session.finished:
            return None

        # Empty input finishes immediately with no steps.
        if len(session.input_string) == 0:
            session.finished = True
            session.rejected_reason = SimulationStatus.REJECTED_EMPTY_INPUT
            return None

        # Already consumed everything.
        if session.cursor >= len(session.input_string):
            session.finished = True
            return None

        symbol = session.input_string[session.cursor]
        step_no = session.cursor + 1
        from_state = session.state

        # --- Invalid symbol short-circuit --------------------------------
        if not is_symbol_in_alphabet(symbol):
            tstep = TransitionStep(
                step=step_no,
                symbol=symbol,
                from_state=from_state,
                to_state=TRAP_STATE,
                is_valid=False,
                explanation=(
                    f"Symbol {symbol!r} is outside the alphabet Sigma."
                ),
            )
            session.trace.append(tstep)
            session.state = TRAP_STATE
            session.cursor += 1
            session.finished = True
            session.rejected_reason = SimulationStatus.REJECTED_INVALID_SYMBOL
            return tstep

        # --- Valid symbol: take the DFA transition -----------------------
        next_state = self._dfa.step(from_state, symbol)

        if from_state == TRAP_STATE:
            is_valid = False
            explanation = "Already in trap state."
        elif next_state == TRAP_STATE:
            is_valid = False
            explanation = f"No valid transition from {from_state} on {symbol!r}."
        else:
            is_valid = True
            explanation = f"{from_state} --{symbol}--> {next_state}"

        tstep = TransitionStep(
            step=step_no,
            symbol=symbol,
            from_state=from_state,
            to_state=next_state,
            is_valid=is_valid,
            explanation=explanation,
        )
        session.trace.append(tstep)
        session.state = next_state
        session.cursor += 1

        # Auto-finish if we trap or exhaust the string.
        if next_state == TRAP_STATE:
            session.finished = True
            session.rejected_reason = SimulationStatus.REJECTED_NO_TRANSITION
        elif session.cursor >= len(session.input_string):
            session.finished = True

        return tstep

    # --- Batch ------------------------------------------------------------

    def run_all(self, session_id: str) -> SimulationResult:
        """
        Finish the remaining steps and return the full SimulationResult.

        If the session never existed, fall back to a fresh one-shot simulate.
        """
        session = self._sessions.get(session_id)
        if session is None:
            return simulate("")

        while not session.finished:
            if self.step(session_id) is None:
                break

        return simulate(session.input_string, dfa=self._dfa)

    def validate(self, input_string: str) -> SimulationResult:
        """One-shot validation delegating to the Minimized DFA simulator."""
        return simulate(input_string, dfa=self._dfa)

    # --- Metadata ---------------------------------------------------------

    def get_metadata(self) -> AutomataMetadata:
        """Return formal DFA description for Page 3 of the GUI."""
        return AutomataMetadata(
            states=list(CANONICAL_STATES),
            alphabet=sorted(ALPHABET),
            start_state=START_STATE,
            accepting_states=sorted(ACCEPTING_STATES),
            transition_table={
                s: dict(CANONICAL_TRANSITIONS.get(s, {}))
                for s in CANONICAL_STATES
            },
            re_pattern=RE_PATTERN,
            minimization_summary={
                "unminimized_states": 18,
                "minimized_states": len(CANONICAL_STATES),
                "states_before": 18,
                "states_after": len(CANONICAL_STATES),
                "merged_groups": (
                    "Canonical DFA is already minimal: all 15 states are "
                    "pairwise distinguishable (see AUTOMATA_THEORY_BASELINE.md)."
                ),
                "note": (
                    "Canonical DFA is already minimal: all 15 states are "
                    "pairwise distinguishable (see AUTOMATA_THEORY_BASELINE.md)."
                ),
                "minimized": True,
            },
        )