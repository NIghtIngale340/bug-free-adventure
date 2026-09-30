"""
EXACT DFA EQUIVALENCE (product automaton)

L(A) = L(B)  iff no reachable pair (p, q) of the product automaton has exactly one of
p in F_A, q in F_B. Breadth-first search explores at most |Q_A| x |Q_B| pairs and returns
the SHORTEST distinguishing word when the languages differ. This is a proof, not a sample.
"""

import itertools
from collections import deque
from dataclasses import dataclass

from app.core.dfa import DFA


@dataclass(frozen=True)
class Equivalence:
    equal: bool
    counterexample: str | None    # shortest word accepted by exactly one automaton
    pairs_explored: int


def dfa_equivalent(a: DFA, b: DFA) -> Equivalence:
    if a.alphabet != b.alphabet:
        raise ValueError("DFAs must share the same alphabet")
    sigma = sorted(a.alphabet)
    start = (a.start_state, b.start_state)
    seen = {start}
    queue = deque([(start, "")])
    while queue:
        (p, q), word = queue.popleft()
        if a.is_accepting(p) != b.is_accepting(q):
            return Equivalence(False, word, len(seen))
        for s in sigma:
            nxt = (a.step(p, s), b.step(q, s))
            if nxt not in seen:
                seen.add(nxt)
                queue.append((nxt, word + s))
    return Equivalence(True, None, len(seen))


def exhaustive_agreement(models: dict, oracle, alphabet, max_len: int) -> tuple[int, dict[str, int]]:
    """
    Compare every model (name -> accepts(word)) with `oracle` on ALL words over `alphabet`
    up to `max_len`. Returns (words checked, {model: number of disagreements}).
    """
    sigma, bad, total = sorted(alphabet), {name: 0 for name in models}, 0
    for n in range(max_len + 1):
        for letters in itertools.product(sigma, repeat=n):
            word = "".join(letters)
            truth = oracle(word)
            total += 1
            for name, accepts in models.items():
                bad[name] += accepts(word) != truth
    return total, bad
