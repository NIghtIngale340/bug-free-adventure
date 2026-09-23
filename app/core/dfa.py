"""
DETERMINISTIC FINITE AUTOMATON (Minimized DFA)
Owner: Ken (Backend / Automata Core Lead)
Task: BE-003

The DFA is the authoritative recognizer of the Employee ID language.

M = (Q, Sigma, delta, q0, F)

Where:
  Q     = 15 states (q0..q13 + q_trap)
  Sigma = 14 symbols
  delta = canonical transition table (from app/data/id_rules.py)
  q0    = 'q0'
  F     = {'q13'}

Layer 2 of the validation pipeline (deterministic simulation).
"""


from app.data.id_rules import (
    ACCEPTING_STATES,
    CANONICAL_STATES,
    CANONICAL_TRANSITIONS,
    START_STATE,
    TRAP_STATE,
)


class DFA:
    """
    Deterministic Finite Automaton.

    If no valid transition exists for a given (state, symbol) pair,
    the automaton moves to q_trap. From q_trap, every symbol loops
    back to q_trap.
    """

    def __init__(
        self,
        states: list[str] | None = None,
        transitions: dict[str, dict[str, str]] | None = None,
        start_state: str = START_STATE,
        accepting_states: set | None = None,
        trap_state: str = TRAP_STATE,
    ) -> None:
        self.states: list[str] = states if states is not None else list(CANONICAL_STATES)
        self.transitions: dict[str, dict[str, str]] = (
            transitions if transitions is not None else CANONICAL_TRANSITIONS
        )
        self.start_state: str = start_state
        self.accepting_states: set = (
            set(accepting_states) if accepting_states is not None else set(ACCEPTING_STATES)
        )
        self.trap_state: str = trap_state

    # --- Core API -----------------------------------------------------------

    def step(self, state: str, symbol: str) -> str:
        """
        Return delta(state, symbol).

        If no explicit transition exists, return q_trap.
        Once in q_trap, every symbol returns q_trap.
        """
        if state == self.trap_state:
            return self.trap_state
        row = self.transitions.get(state, {})
        return row.get(symbol, self.trap_state)

    def is_accepting(self, state: str) -> bool:
        return state in self.accepting_states

    def run(self, input_string: str) -> str:
        """Return the final state after consuming every symbol."""
        state = self.start_state
        for symbol in input_string:
            state = self.step(state, symbol)
        return state

    def accepts(self, input_string: str) -> bool:
        return self.is_accepting(self.run(input_string))

    # --- Inspection ---------------------------------------------------------

    def transition_table(self) -> dict[str, dict[str, str]]:
        """Return the full delta as a nested dict for display."""
        return {state: dict(self.transitions.get(state, {})) for state in self.states}