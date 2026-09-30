"""
DFA MINIMIZATION (Moore partition refinement)

  1. remove states unreachable from q0
  2. P0 = { F, Q \\ F }
  3. split every block whose members disagree, for some symbol, on the block of their
     successor; repeat until no block splits (each pass is recorded as a "round")
  4. merge each final block into one state; rename by BFS order q0, q1, ... (dead block q_trap)

Moore's algorithm (O(n^2 |Sigma|)) is used, not Hopcroft's worklist variant (O(n log n));
both compute the same partition and n = 15 here.
"""

from collections import deque
from dataclasses import dataclass

from app.core.dfa import DFA, natural_key


@dataclass(frozen=True)
class MinimizationResult:
    dfa: DFA
    removed_unreachable: tuple[str, ...]
    rounds: tuple[tuple[tuple[str, ...], ...], ...]   # rounds[k] = partition P_k (original names)
    state_map: dict[str, str]                         # original state -> minimized state
    merged_groups: tuple[tuple[str, ...], ...]        # blocks with more than one member
    states_before: int
    states_after: int


def _reachable(dfa: DFA) -> list[str]:
    seen, queue = [dfa.start_state], deque([dfa.start_state])
    while queue:
        for nxt in dfa.transitions[queue.popleft()].values():
            if nxt not in seen:
                seen.append(nxt)
                queue.append(nxt)
    return seen


def _partition(block_of: dict[str, int]) -> tuple[tuple[str, ...], ...]:
    blocks: dict[int, list[str]] = {}
    for s, b in block_of.items():
        blocks.setdefault(b, []).append(s)
    return tuple(sorted((tuple(sorted(m, key=natural_key)) for m in blocks.values()),
                        key=lambda m: natural_key(m[0])))


def minimize(dfa: DFA, prefix: str = "q", dead_name: str = "q_trap") -> MinimizationResult:
    reachable = set(_reachable(dfa))
    removed = tuple(s for s in dfa.states if s not in reachable)
    states = [s for s in dfa.states if s in reachable]
    sigma = sorted(dfa.alphabet)

    block_of = {s: 0 if dfa.is_accepting(s) else 1 for s in states}
    rounds = [_partition(block_of)]
    while True:
        ids: dict[tuple, int] = {}
        refined = {
            s: ids.setdefault((block_of[s], *(block_of[dfa.step(s, a)] for a in sigma)), len(ids))
            for s in states
        }
        if len(ids) == len(set(block_of.values())):
            break
        block_of = refined
        rounds.append(_partition(block_of))

    # Name blocks: BFS from the start block over sorted symbols; dead blocks -> dead_name.
    rep = {b: next(s for s in states if block_of[s] == b) for b in set(block_of.values())}
    dead_blocks = {b for b, s in rep.items() if dfa.is_dead(s)}
    order, queue = [block_of[dfa.start_state]], deque([block_of[dfa.start_state]])
    while queue:
        for a in sigma:
            b = block_of[dfa.step(rep[queue[0]], a)]
            if b not in order and b not in dead_blocks:
                order.append(b)
                queue.append(b)
        queue.popleft()
    names = {b: f"{prefix}{i}" for i, b in enumerate(order)}
    names.update({b: dead_name if len(dead_blocks) == 1 else f"{dead_name}{i}"
                  for i, b in enumerate(sorted(dead_blocks))})

    min_states = [names[b] for b in order if b not in dead_blocks] + [names[b] for b in sorted(dead_blocks)]
    transitions = {
        names[b]: {a: names[block_of[dfa.step(rep[b], a)]] for a in sigma}
        for b in list(order) + sorted(dead_blocks)
    }
    accepting = {names[block_of[s]] for s in states if dfa.is_accepting(s)}
    minimized = DFA(min_states, sigma, transitions, names[block_of[dfa.start_state]], accepting)

    state_map = {s: names[block_of[s]] for s in states}
    merged = tuple(m for m in rounds[-1] if len(m) > 1)
    return MinimizationResult(minimized, removed, tuple(rounds), state_map, merged,
                              len(dfa.states), len(min_states))
