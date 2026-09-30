"""
SYMBOL-BY-SYMBOL RUN ENGINE (DFA or NFA)

`Run` is the ONE implementation of stepping, tracing and result-building. simulate() is a
loop over it and SimulationService sessions wrap it, so the animated GUI and the one-shot
validator cannot drift apart.

Rules
  - empty input               -> REJECTED_EMPTY_INPUT (automaton not started)
  - any symbol outside Sigma   -> REJECTED_INVALID_SYMBOL. Layer 1 checks the WHOLE string
                                  first; the automaton is not started, no transition is taken
  - run reaches a dead state   -> REJECTED_NO_TRANSITION (DFA) / empty set (NFA), stops there
  - input consumed in F        -> ACCEPTED, otherwise REJECTED_NON_FINAL_STATE
"""

from app.core.dfa import DFA
from app.core.language import describe_symbols, validate_symbols
from app.core.models import SimulationResult, SimulationStatus, TransitionStep
from app.core.nfa import NFA
from app.core.pipeline import get_pipeline


def format_subset(states) -> str:
    return "{" + ", ".join(sorted(states, key=lambda s: (len(s), s))) + "}" if states else "∅"


class Run:
    def __init__(self, input_string: str, machine: DFA | NFA | None = None) -> None:
        self.machine = machine if machine is not None else get_pipeline().min_dfa
        self.is_nfa = isinstance(machine, NFA)
        self.input = input_string
        self.reset()

    # --- lifecycle ------------------------------------------------------------

    def reset(self) -> None:
        self.cursor = 0
        self.trace: list[TransitionStep] = []
        self.finished = False
        self._result: SimulationResult | None = None
        self.illegal: list[tuple[int, str]] = []
        m = self.machine
        self.active: frozenset[str] = m.start_closure() if self.is_nfa else frozenset({m.start_state})

        if not self.input:
            self._finish(SimulationStatus.REJECTED_EMPTY_INPUT, None, None,
                         "Input string cannot be empty.", "Please enter an Employee ID.")
            return
        _, self.illegal = validate_symbols(self.input)
        if self.illegal:
            listing = ", ".join(f"{ch!r} at position {i}" for i, ch in self.illegal)
            self._finish(
                SimulationStatus.REJECTED_INVALID_SYMBOL, None, self.illegal[0][0],
                f"Not in Σ: {listing}.",
                f"Rejected before the automaton ran: {listing} — not in the alphabet Σ, "
                "so the input is not a string over Σ.",
            )

    @property
    def state_label(self) -> str:
        return format_subset(self.active) if self.is_nfa else next(iter(self.active))

    # --- stepping -------------------------------------------------------------

    def step(self) -> TransitionStep | None:
        """Consume one symbol; None once the run has finished."""
        if self.finished:
            return None
        m, idx = self.machine, self.cursor
        symbol = self.input[idx]
        src = self.state_label
        prev = self.active

        if self.is_nfa:
            self.active = m.step(prev, symbol)
            dst, dead = format_subset(self.active), not self.active
            expected = m.expected(prev)
        else:
            nxt = m.step(src, symbol)
            self.active = frozenset({nxt})
            dst, dead = nxt, m.is_dead(nxt)
            expected = m.expected(src)
        self.cursor += 1

        if dead:
            why = f"No transition: {src} expects {describe_symbols(expected)} but read {symbol!r}."
        else:
            why = f"{src} --{symbol}--> {dst}"
        step = TransitionStep(idx + 1, symbol, src, dst, not dead, why)
        self.trace.append(step)

        if dead:
            self._finish(SimulationStatus.REJECTED_NO_TRANSITION, dst, idx,
                         f"No valid transition on {symbol!r} at position {idx}.",
                         f"Rejected at position {idx}: {why}")
        elif self.cursor == len(self.input):
            self._finish_consumed(dst)
        return step

    def _finish_consumed(self, final: str) -> None:
        m = self.machine
        accepted = bool(self.active & m.accepting_states) if self.is_nfa else m.is_accepting(final)
        if accepted:
            self._finish(SimulationStatus.ACCEPTED, final, None, None,
                         "Accepted: the input was consumed and the run ended in an accepting state.")
            return
        needed = m.symbols_needed(self.active if self.is_nfa else final)
        expected = m.expected(self.active if self.is_nfa else final)
        self._finish(
            SimulationStatus.REJECTED_NON_FINAL_STATE, final, None,
            f"Input ended in non-accepting state {final}.",
            f"Rejected: input ended in {final}, which is not accepting — at least {needed} more "
            f"symbol(s) needed (expected {describe_symbols(expected)}).",
        )

    def _finish(self, status, final, err_pos, err_msg, explanation) -> None:
        self.finished = True
        self._result = SimulationResult(
            input_string=self.input, accepted=status is SimulationStatus.ACCEPTED, status=status,
            final_state=final, trace=list(self.trace), error_message=err_msg,
            error_position=err_pos, processed_symbols=self.cursor, total_symbols=len(self.input),
            explanation=explanation,
        )

    def result(self) -> SimulationResult:
        """Drain any remaining symbols and return the final SimulationResult."""
        while self.step() is not None:
            pass
        assert self._result is not None
        return self._result


def simulate(input_string: str, machine: DFA | NFA | None = None) -> SimulationResult:
    """One-shot run on the minimal DFA (default), or on any DFA / NFA passed in."""
    return Run(input_string, machine).result()


def simulate_nfa(input_string: str, nfa: NFA | None = None) -> SimulationResult:
    return simulate(input_string, nfa or get_pipeline().nfa)
