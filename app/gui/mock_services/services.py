
from dataclasses import dataclass, field
import uuid

from app.gui.mock_core.models import (
    SimulationResult,
    SimulationStatus,
    TransitionStep,
    AutomataMetadata,
)

TRAP = "q_trap"
_TRANSITIONS: dict[tuple[str, str], str] = {}


def _digits() -> list[str]:
    return [str(d) for d in range(10)]


def _build_transitions() -> None:
    # EMP-YYYY-NNNN
    _TRANSITIONS[("q0", "E")] = "q1"
    _TRANSITIONS[("q1", "M")] = "q2"
    _TRANSITIONS[("q2", "P")] = "q3"
    _TRANSITIONS[("q3", "-")] = "q4"

    year_chain = ["q4", "q5", "q6", "q7", "q8"]
    for a, b in zip(year_chain, year_chain[1:]):
        for d in _digits():
            _TRANSITIONS[(a, d)] = b

    _TRANSITIONS[("q8", "-")] = "q9"

    num_chain = ["q9", "q10", "q11", "q12", "q13"]
    for a, b in zip(num_chain, num_chain[1:]):
        for d in _digits():
            _TRANSITIONS[(a, d)] = b


_build_transitions()

ALPHABET = ["E", "M", "P", "-"] + _digits()
STATES = ["q0", "q1", "q2", "q3", "q4", "q5", "q6", "q7", "q8",
          "q9", "q10", "q11", "q12", "q13", TRAP]
ACCEPTING = ["q13"]
START = "q0"


def _delta(state: str, symbol: str) -> str:
    return _TRANSITIONS.get((state, symbol), TRAP)


def _describe(symbol: str, from_state: str, to_state: str) -> str:
    if to_state == TRAP:
        return f"No valid transition for '{symbol}' from {from_state} -> trapped"
    return f"Consumed '{symbol}': {from_state} -> {to_state}"


def _run_full_trace(input_string: str) -> list[TransitionStep]:
    trace: list[TransitionStep] = []
    state = START
    for i, ch in enumerate(input_string, start=1):
        nxt = _delta(state, ch)
        trace.append(TransitionStep(
            step=i, symbol=ch, from_state=state, to_state=nxt,
            is_valid=nxt != TRAP, description=_describe(ch, state, nxt),
        ))
        state = nxt
    return trace


@dataclass
class _Session:
    input_string: str
    position: int = 0
    current_state: str = START
    trace: list[TransitionStep] = field(default_factory=list)


class MockAutomataService:
    """Drop-in stand-in for ValidationService + SimulationService."""

    def __init__(self) -> None:
        self._sessions: dict[str, _Session] = {}

    # Validator Dashboard
    def validate(self, input_string: str) -> SimulationResult:
        if not input_string:
            return SimulationResult(
                input_string="", accepted=False,
                status=SimulationStatus.REJECTED_EMPTY_INPUT,
                final_state=None, trace=[],
                error_message="Input string cannot be empty.",
                error_position=None, processed_symbols=0, total_symbols=0,
                explanation="Please enter an Employee ID.",
            )

        for i, ch in enumerate(input_string):
            if ch not in ALPHABET:
                trace = _run_full_trace(input_string[: i + 1])
                return SimulationResult(
                    input_string=input_string, accepted=False,
                    status=SimulationStatus.REJECTED_INVALID_SYMBOL,
                    final_state=trace[-1].to_state, trace=trace,
                    error_message=f"'{ch}' is not part of the alphabet Σ.",
                    error_position=i, processed_symbols=i + 1,
                    total_symbols=len(input_string),
                    explanation=f"Rejected at position {i}: invalid symbol '{ch}'.",
                )

        trace = _run_full_trace(input_string)
        final_state = trace[-1].to_state if trace else START
        accepted = final_state in ACCEPTING

        if accepted:
            status = SimulationStatus.ACCEPTED
            explanation = f"Accepted: reached final state {final_state}."
            error_message = None
            error_position = None
        elif final_state == TRAP:
            status = SimulationStatus.REJECTED_TRAP_STATE
            trap_index = next(i for i, t in enumerate(trace) if t.to_state == TRAP)
            error_position = trap_index
            error_message = "String does not match the EMP-YYYY-NNNN structure."
            explanation = f"Rejected: fell dead state at step {trap_index + 1}."
        else:
            status = SimulationStatus.REJECTED_NON_FINAL_STATE
            error_message = "Input ended before reaching an accepting state."
            error_position = len(input_string) - 1
            explanation = f"Rejected: stopped at non-final state {final_state}."

        return SimulationResult(
            input_string=input_string, accepted=accepted, status=status,
            final_state=final_state, trace=trace, error_message=error_message,
            error_position=error_position, processed_symbols=len(input_string),
            total_symbols=len(input_string), explanation=explanation,
        )

    # Step-by-Step Simulator
    def create_session(self, input_string: str) -> str:
        session_id = str(uuid.uuid4())
        self._sessions[session_id] = _Session(input_string=input_string)
        return session_id

    def step(self, session_id: str) -> TransitionStep | None:
        session = self._sessions.get(session_id)
        if session is None or session.position >= len(session.input_string):
            return None

        ch = session.input_string[session.position]
        from_state = session.current_state
        to_state = _delta(from_state, ch) if ch in ALPHABET else TRAP

        transition = TransitionStep(
            step=session.position + 1, symbol=ch, from_state=from_state,
            to_state=to_state, is_valid=to_state != TRAP,
            description=_describe(ch, from_state, to_state),
        )
        session.trace.append(transition)
        session.current_state = to_state
        session.position += 1
        return transition

    def run_all(self, session_id: str) -> SimulationResult:
        session = self._sessions.get(session_id)
        if session is None:
            return self.validate("")
        while self.step(session_id) is not None:
            pass
        return self.validate(session.input_string)

    def reset(self, session_id: str) -> None:
        if session_id in self._sessions:
            self._sessions[session_id] = _Session(
                input_string=self._sessions[session_id].input_string
            )

    # Automata Theory Explorer
    def get_metadata(self) -> AutomataMetadata:
        table: dict[str, dict[str, str]] = {}
        for (state, symbol), nxt in _TRANSITIONS.items():
            table.setdefault(state, {})[symbol] = nxt

        return AutomataMetadata(
            states=STATES, alphabet=ALPHABET, start_state=START,
            accepting_states=ACCEPTING, transition_table=table,
            re_pattern=r"^EMP-[0-9]{4}-[0-9]{4}$",
            minimization_summary={
                "unminimized_states": 18,
                "minimized_states": len(STATES),
                "merged_groups": "Digit-chain states merge only where "
                                 "transition behavior is identical; "
                                 "positional digit states stay distinct "
                                 "because each leads to a different "
                                 "acceptance path.",
            },
        )