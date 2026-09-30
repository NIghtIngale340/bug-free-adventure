"""
NFA WITH EPSILON TRANSITIONS, THOMPSON CONSTRUCTION AND SUBSET CONSTRUCTION

    RE  --thompson()-->  epsilon-NFA  --subset_construction()-->  DFA  --minimize()--> min DFA

The NFA is *built from the regular expression* (app/core/regex.py). Concatenation is joined
with epsilon edges, so epsilon-closure is exercised for real. A missing NFA transition means
the empty set (an NFA has no trap state); the dead state only appears when subset construction
completes the DFA.
"""

import itertools
from collections import deque
from collections.abc import Iterable
from dataclasses import dataclass

from app.core.dfa import DFA, dist_to_accept, natural_key
from app.core.regex import Class, Concat, Lit, Node, Repeat


class NFA:
    """
    delta:   {state: {symbol: {next_states}}}
    epsilon: {state: {next_states}}
    """

    def __init__(
        self,
        states: list[str],
        transitions: dict[str, dict[str, set[str]]],
        start_state: str,
        accepting_states: Iterable[str],
        epsilon: dict[str, set[str]] | None = None,
    ) -> None:
        self.states = list(states)
        self.transitions = {s: {a: set(t) for a, t in transitions.get(s, {}).items()} for s in states}
        self.epsilon = {s: set((epsilon or {}).get(s, ())) for s in states}
        self.start_state = start_state
        self.accepting_states = frozenset(accepting_states)
        self.alphabet: frozenset[str] = frozenset(a for row in self.transitions.values() for a in row)
        self._dist = dist_to_accept(
            self.states,
            [(u, v, 1) for u, row in self.transitions.items() for ts in row.values() for v in ts]
            + [(u, v, 0) for u, ts in self.epsilon.items() for v in ts],
            self.accepting_states,
        )

    # --- Core operations ----------------------------------------------------

    def start_closure(self) -> frozenset[str]:
        return epsilon_closure(self, {self.start_state})

    def step(self, subset: Iterable[str], symbol: str) -> frozenset[str]:
        """epsilon-closure(move(subset, symbol))."""
        return epsilon_closure(self, move(self, subset, symbol))

    def accepts(self, word: str) -> bool:
        current = self.start_closure()
        for symbol in word:
            current = self.step(current, symbol)
            if not current:
                return False
        return bool(current & self.accepting_states)

    # --- Inspection ---------------------------------------------------------

    def expected(self, subset: Iterable[str]) -> list[str]:
        """Symbols that have a move from at least one state of `subset`."""
        return sorted({a for s in subset for a, t in self.transitions[s].items() if t})

    def symbols_needed(self, subset: Iterable[str]) -> int | None:
        ds = [self._dist[s] for s in subset if s in self._dist]
        return min(ds) if ds else None

    @property
    def epsilon_edge_count(self) -> int:
        return sum(len(t) for t in self.epsilon.values())


def epsilon_closure(nfa: NFA, states: Iterable[str]) -> frozenset[str]:
    closure = set(states)
    stack = list(closure)
    while stack:
        for nxt in nfa.epsilon.get(stack.pop(), ()):
            if nxt not in closure:
                closure.add(nxt)
                stack.append(nxt)
    return frozenset(closure)


def move(nfa: NFA, states: Iterable[str], symbol: str) -> frozenset[str]:
    return frozenset(t for s in states for t in nfa.transitions[s].get(symbol, ()))


# --- Thompson construction ----------------------------------------------------


def thompson(node: Node) -> NFA:
    """
    Build an epsilon-NFA from the RE. Every atom (Lit or Class) becomes two states joined by
    its symbol(s); concatenation joins consecutive fragments with an epsilon edge.
    A Class is Thompson's union (0 ∪ 1 ∪ ... ∪ 9) collapsed into one atom with one edge per
    symbol (the standard character-class shortcut, avoiding 10 parallel branches per digit).
    """
    counter = itertools.count()
    trans: dict[str, dict[str, set[str]]] = {}
    eps: dict[str, set[str]] = {}

    def new() -> str:
        s = f"n{next(counter)}"
        trans[s], eps[s] = {}, set()
        return s

    def build(n: Node) -> tuple[str, str]:
        match n:
            case Lit(c):
                s, e = new(), new()
                trans[s][c] = {e}
                return s, e
            case Class(chars):
                s, e = new(), new()
                for c in chars:
                    trans[s][c] = {e}
                return s, e
            case Repeat(inner, k):
                return build(Concat((inner,) * k))
            case Concat(parts):
                frags = [build(p) for p in parts]
                for (_, end), (start, _) in zip(frags, frags[1:]):
                    eps[end].add(start)
                return frags[0][0], frags[-1][1]

    start, end = build(node)
    return NFA(list(trans), trans, start, {end}, eps)


# --- Subset construction ------------------------------------------------------


@dataclass(frozen=True)
class SubsetMove:
    """One row of the conversion: symbols with the same outcome are grouped."""
    symbols: tuple[str, ...]
    move: frozenset[str]          # move(subset, a)
    closure: frozenset[str]       # epsilon-closure(move(subset, a))
    target: str                   # DFA state name ("D_trap" for the empty set)


@dataclass(frozen=True)
class SubsetStep:
    name: str
    subset: frozenset[str]
    accepting: bool
    moves: tuple[SubsetMove, ...]


DEAD_NAME = "D_trap"


def subset_construction(nfa: NFA) -> tuple[DFA, list[SubsetStep]]:
    """
    Rabin-Scott subset construction. Returns the COMPLETE DFA (the empty subset becomes an
    explicit dead state D_trap) and a step log with move / epsilon-closure per symbol group.
    """
    sigma = sorted(nfa.alphabet)
    start = nfa.start_closure()
    names: dict[frozenset[str], str] = {start: "D0"}
    queue = deque([start])
    steps: list[SubsetStep] = []
    transitions: dict[str, dict[str, str]] = {}
    dead_needed = False

    while queue:
        current = queue.popleft()
        groups: dict[tuple[frozenset[str], frozenset[str]], list[str]] = {}
        for a in sigma:
            mv = move(nfa, current, a)
            groups.setdefault((mv, epsilon_closure(nfa, mv)), []).append(a)

        moves, row = [], {}
        for (mv, clo), symbols in groups.items():
            if clo:
                if clo not in names:
                    names[clo] = f"D{len(names)}"
                    queue.append(clo)
                target = names[clo]
            else:
                target, dead_needed = DEAD_NAME, True
            moves.append(SubsetMove(tuple(symbols), mv, clo, target))
            row.update({a: target for a in symbols})
        transitions[names[current]] = row
        steps.append(SubsetStep(
            names[current], current, bool(current & nfa.accepting_states),
            tuple(sorted(moves, key=lambda m: m.symbols)),
        ))

    states = sorted(names.values(), key=natural_key)
    if dead_needed:
        states.append(DEAD_NAME)
        transitions[DEAD_NAME] = {a: DEAD_NAME for a in sigma}
    steps.sort(key=lambda s: natural_key(s.name))
    if dead_needed:  # the empty subset: every symbol leads back to itself
        steps.append(SubsetStep(DEAD_NAME, frozenset(), False,
                                (SubsetMove(tuple(sigma), frozenset(), frozenset(), DEAD_NAME),)))
    accepting = {names[s] for s in names if s & nfa.accepting_states}
    return DFA(states, sigma, transitions, "D0", accepting), steps
