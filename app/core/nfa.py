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