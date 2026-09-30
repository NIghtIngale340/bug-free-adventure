"""
DETERMINISTIC FINITE AUTOMATON

M = (Q, Sigma, delta, q0, F)  with delta TOTAL: every (state, symbol) pair is defined
explicitly (dead-state edges included), so there is no implicit "missing = trap" rule.
The constructor validates the five-tuple. A DFA is never hand-typed for the simulator:
it is produced by subset_construction() and minimize() (see app/core/pipeline.py).
"""

import re
from collections.abc import Iterable


def natural_key(name: str) -> tuple:
    """Sort key so q2 < q10 and D2 < D10."""
    return tuple(int(t) if t.isdigit() else t for t in re.split(r"(\d+)", name))


def dist_to_accept(
    states: Iterable[str], edges: Iterable[tuple[str, str, int]], accepting: Iterable[str]
) -> dict[str, int]:
    """Fewest symbols needed to reach an accepting state (edge cost 0 = epsilon, 1 = symbol)."""
    accepting = set(accepting)
    dist = {s: (0 if s in accepting else None) for s in states}
    edges = list(edges)
    changed = True
    while changed:
        changed = False
        for u, v, cost in edges:
            if dist[v] is not None and (dist[u] is None or dist[v] + cost < dist[u]):
                dist[u] = dist[v] + cost
                changed = True
    return {s: d for s, d in dist.items() if d is not None}


class DFA:
    def __init__(
        self,
        states: list[str],
        alphabet: Iterable[str],
        transitions: dict[str, dict[str, str]],
        start_state: str,
        accepting_states: Iterable[str],
    ) -> None:
        self.states: list[str] = list(states)
        self.alphabet: frozenset[str] = frozenset(alphabet)
        self.transitions: dict[str, dict[str, str]] = {
            s: dict(transitions.get(s, {})) for s in self.states
        }
        self.start_state = start_state
        self.accepting_states: frozenset[str] = frozenset(accepting_states)
        self._validate()
        self._dist = dist_to_accept(
            self.states,
            ((u, v, 1) for u, row in self.transitions.items() for v in row.values()),
            self.accepting_states,
        )
        # Dead (trap) states: no accepting state is reachable from them.
        self.dead_states: frozenset[str] = frozenset(s for s in self.states if s not in self._dist)

    def _validate(self) -> None:
        known = set(self.states)
        if len(known) != len(self.states):
            raise ValueError("duplicate state names")
        if self.start_state not in known:
            raise ValueError(f"start state {self.start_state!r} not in Q")
        if not self.accepting_states <= known:
            raise ValueError(f"accepting states not in Q: {sorted(self.accepting_states - known)}")
        for s, row in self.transitions.items():
            for a, t in row.items():
                if a not in self.alphabet or t not in known:
                    raise ValueError(f"bad transition delta({s!r}, {a!r}) = {t!r}")
            missing = self.alphabet - row.keys()
            if missing:
                raise ValueError(f"delta not total: {s!r} lacks {sorted(missing)}")

    # --- Core API -----------------------------------------------------------

    def step(self, state: str, symbol: str) -> str:
        """delta(state, symbol). Symbols outside Sigma are not in delta's domain."""
        if symbol not in self.alphabet:
            raise ValueError(f"symbol {symbol!r} is not in Sigma")
        return self.transitions[state][symbol]

    def is_accepting(self, state: str) -> bool:
        return state in self.accepting_states

    def is_dead(self, state: str) -> bool:
        return state in self.dead_states

    def run(self, word: str) -> str:
        state = self.start_state
        for symbol in word:
            state = self.step(state, symbol)
        return state

    def accepts(self, word: str) -> bool:
        """w in L(M). A word containing a symbol outside Sigma is not a word over Sigma."""
        if not set(word) <= self.alphabet:
            return False
        return self.is_accepting(self.run(word))

    # --- Inspection ---------------------------------------------------------

    def expected(self, state: str) -> list[str]:
        """Symbols that keep the run alive (lead to a non-dead state)."""
        return sorted(a for a, t in self.transitions[state].items() if t not in self.dead_states)

    def symbols_needed(self, state: str) -> int | None:
        """Fewest more symbols needed to accept from `state` (None if dead)."""
        return self._dist.get(state)

    def transition_table(self) -> dict[str, dict[str, str]]:
        return {s: dict(self.transitions[s]) for s in self.states}
