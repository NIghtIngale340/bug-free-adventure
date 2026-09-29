"""
NON-DETERMINISTIC FINITE AUTOMATON + SUBSET CONSTRUCTION
Owner: Ken (Backend / Automata Core Lead)
Task: BE-003

For the Employee ID language, the NFA is structurally identical to the
DFA because the language is a straight-line concatenation with no
branching. We still model it explicitly so the pipeline
RE -> NFA -> DFA -> Minimized DFA is visible in the code and in the
written documentation.

Subset construction is implemented generally, so if the NFA is later
extended with epsilon transitions or multiple moves, the conversion
still works.
"""

from collections import deque

from app.core.dfa import DFA
from app.core.language import is_symbol_in_alphabet
from app.core.models import (
    SimulationResult,
    SimulationStatus,
    TransitionStep,
)
from app.data.id_rules import (
    ACCEPTING_STATES,
    CANONICAL_STATES,
    CANONICAL_TRANSITIONS,
    START_STATE,
)


class NFA:
    """
    NFA with explicit epsilon transitions.

    delta is stored as:
        { state: { symbol: {next_states...} } }
    and epsilon transitions as:
        { state: {next_states...} }
    """

    def __init__(
        self,
        states: list[str],
        transitions: dict[str, dict[str, set[str]]],
        start_state: str,
        accepting_states: set[str],
        epsilon: dict[str, set[str]] | None = None,
    ) -> None:
        self.states = states
        self.transitions = transitions
        self.start_state = start_state
        self.accepting_states = set(accepting_states)
        self.epsilon = epsilon or {s: set() for s in states}


def canonical_nfa() -> NFA:
    """
    Build the canonical NFA for EMP-YYYY-NNNN.

    Because the language is a pure concatenation, the NFA has exactly
    one move per (state, symbol) pair, making subset construction a
    trivial 1-to-1 mapping. This is documented in docs/nfa.md.
    """
    transitions: dict[str, dict[str, set[str]]] = {s: {} for s in CANONICAL_STATES}
    for state, row in CANONICAL_TRANSITIONS.items():
        for symbol, nxt in row.items():
            transitions.setdefault(state, {}).setdefault(symbol, set()).add(nxt)
    return NFA(
        states=list(CANONICAL_STATES),
        transitions=transitions,
        start_state=START_STATE,
        accepting_states=set(ACCEPTING_STATES),
    )


def epsilon_closure(nfa: NFA, states: set[str]) -> set[str]:
    """Return the epsilon closure of `states`."""
    stack = list(states)
    closure = set(states)
    while stack:
        s = stack.pop()
        for nxt in nfa.epsilon.get(s, set()):
            if nxt not in closure:
                closure.add(nxt)
                stack.append(nxt)
    return closure


def move(nfa: NFA, states: set[str], symbol: str) -> set[str]:
    """Return the set of NFA states reachable from `states` on `symbol`."""
    result: set[str] = set()
    for s in states:
        result |= nfa.transitions.get(s, {}).get(symbol, set())
    return result


def subset_construction(nfa: NFA) -> tuple[DFA, list[tuple[str, set[str]]]]:
    """
    Convert an NFA to a DFA via the subset construction algorithm.

    Returns:
        (dfa, trace)
        where `trace` lists every DFA state created and the NFA subset
        it represents. This trace is used in docs/dfa.md for the defense.
    """
    start = frozenset(epsilon_closure(nfa, {nfa.start_state}))
    dfa_states: dict[frozenset, str] = {start: "D0"}
    dfa_transitions: dict[str, dict[str, str]] = {"D0": {}}
    trace: list[tuple[str, set[str]]] = [("D0", set(start))]

    queue = deque([start])
    counter = 1

    while queue:
        current = queue.popleft()
        current_name = dfa_states[current]

        # Gather every symbol that appears in any NFA state of `current`.
        symbols: set[str] = set()
        for s in current:
            symbols |= set(nfa.transitions.get(s, {}).keys())

        for symbol in sorted(symbols):
            nxt = frozenset(epsilon_closure(nfa, move(nfa, set(current), symbol)))
            if not nxt:
                continue
            if nxt not in dfa_states:
                name = f"D{counter}"
                counter += 1
                dfa_states[nxt] = name
                dfa_transitions[name] = {}
                trace.append((name, set(nxt)))
                queue.append(nxt)
            dfa_transitions[current_name][symbol] = dfa_states[nxt]

    # Mark trap: any state that is not accepting has no outgoing on some symbol -> add D_trap.
    dfa_transitions.setdefault("D_trap", {})

    dfa_accepting = {
        dfa_states[subset]
        for subset in dfa_states
        if subset & nfa.accepting_states
    }

    dfa = DFA(
        states=list(dfa_states.values()) + ["D_trap"],
        transitions=dfa_transitions,
        start_state="D0",
        accepting_states=dfa_accepting,
        trap_state="D_trap",
    )
    return dfa, trace


def _format_subset(states: set[str] | frozenset[str]) -> str:
    """Format an NFA state subset as mathematical set notation {q0, q1} or ∅."""
    if not states:
        return "∅"
    return "{" + ", ".join(sorted(states)) + "}"


def simulate_nfa(input_string: str, nfa: NFA | None = None) -> SimulationResult:
    """
    Run `input_string` through the Canonical NFA tracking active subsets.

    Rules:
      - Empty input      -> REJECTED_EMPTY_INPUT, final_state=None
      - Symbol outside Σ -> REJECTED_INVALID_SYMBOL, to_state="∅"
      - No valid move    -> transition to ∅, REJECTED_NO_TRANSITION
      - Ends in subset containing q13 -> ACCEPTED
      - Ends elsewhere   -> REJECTED_NON_FINAL_STATE
    """
    nfa = nfa or canonical_nfa()
    trace: list[TransitionStep] = []
    total = len(input_string)

    if total == 0:
        return SimulationResult(
            input_string="",
            accepted=False,
            status=SimulationStatus.REJECTED_EMPTY_INPUT,
            final_state=None,
            trace=[],
            error_message="Input string cannot be empty.",
            error_position=None,
            processed_symbols=0,
            total_symbols=0,
            explanation="Please enter an Employee ID.",
        )

    current_subset = epsilon_closure(nfa, {nfa.start_state})
    state_str = _format_subset(current_subset)

    for idx, symbol in enumerate(input_string):
        step_no = idx + 1

        if not is_symbol_in_alphabet(symbol):
            trace.append(
                TransitionStep(
                    step=step_no,
                    symbol=symbol,
                    from_state=state_str,
                    to_state="∅",
                    is_valid=False,
                    explanation=f"Symbol {symbol!r} is outside the alphabet Sigma.",
                )
            )
            return SimulationResult(
                input_string=input_string,
                accepted=False,
                status=SimulationStatus.REJECTED_INVALID_SYMBOL,
                final_state="∅",
                trace=trace,
                error_message=f"Invalid symbol {symbol!r} at position {idx}.",
                error_position=idx,
                processed_symbols=step_no,
                total_symbols=total,
                explanation=f"Rejected: {symbol!r} is not part of the Employee ID alphabet.",
            )

        # Valid symbol: compute move + epsilon closure
        next_subset = epsilon_closure(nfa, move(nfa, current_subset, symbol))
        to_state_str = _format_subset(next_subset)
        is_valid = bool(next_subset)

        if not is_valid:
            trace.append(
                TransitionStep(
                    step=step_no,
                    symbol=symbol,
                    from_state=state_str,
                    to_state="∅",
                    is_valid=False,
                    explanation=f"No valid NFA transition from {state_str} on {symbol!r}.",
                )
            )
            return SimulationResult(
                input_string=input_string,
                accepted=False,
                status=SimulationStatus.REJECTED_NO_TRANSITION,
                final_state="∅",
                trace=trace,
                error_message=f"No valid transition from NFA subset {state_str} on {symbol!r} at position {idx}.",
                error_position=idx,
                processed_symbols=step_no,
                total_symbols=total,
                explanation=f"Rejected: no NFA transition on {symbol!r} at position {idx}.",
            )

        trace.append(
            TransitionStep(
                step=step_no,
                symbol=symbol,
                from_state=state_str,
                to_state=to_state_str,
                is_valid=True,
                explanation=f"{state_str} --{symbol}--> {to_state_str}",
            )
        )
        current_subset = next_subset
        state_str = to_state_str

    accepted = bool(current_subset & nfa.accepting_states)
    if accepted:
        status = SimulationStatus.ACCEPTED
        explanation = "Input recognized as a valid Employee ID by Canonical NFA."
    else:
        status = SimulationStatus.REJECTED_NON_FINAL_STATE
        explanation = (
            f"Input ended in non-accepting NFA subset {state_str}; expected {sorted(nfa.accepting_states)}."
        )

    return SimulationResult(
        input_string=input_string,
        accepted=accepted,
        status=status,
        final_state=state_str,
        trace=trace,
        error_message=None if accepted else f"Non-accepting NFA subset {state_str}.",
        error_position=None if accepted else total - 1,
        processed_symbols=total,
        total_symbols=total,
        explanation=explanation,
    )