"""
DFA MINIMIZATION (HOPCROFT PARTITION REFINEMENT)
Owner: Ken (Backend / Automata Core Lead)
Task: BE-004

Minimizes a DFA by:
  1. Removing unreachable states.
  2. Partition refinement (Hopcroft / Moore) until stable.
  3. Merging equivalent states.
  4. Recording a trace for the academic defense.

For the Employee ID language, the canonical DFA is ALREADY minimal
(see AUTOMATA_THEORY_BASELINE.md section 4). This module still performs
the full algorithm so the minimization step of the pipeline is
demonstrated in code and can be pointed to during the defense.
"""


from app.core.dfa import DFA


def _reachable_states(dfa: DFA) -> set[str]:
    """Return the set of states reachable from the start state.

    Note: q_trap is reachable *implicitly* from any state that is missing
    an explicit transition on some symbol in Sigma. Since the canonical
    DFA has empty rows for q13 and q_trap, we always include the trap
    state in the reachable set if it exists in the state list.
    """
    seen: set[str] = set()
    stack: list[str] = [dfa.start_state]
    while stack:
        s = stack.pop()
        if s in seen:
            continue
        seen.add(s)
        for nxt in dfa.transitions.get(s, {}).values():
            if nxt not in seen:
                stack.append(nxt)
    if dfa.trap_state in dfa.states:
        seen.add(dfa.trap_state)
    return seen


def _prune_unreachable(dfa: DFA) -> tuple[DFA, list[str]]:
    """Return a new DFA with only reachable states, plus the removed list."""
    reachable = _reachable_states(dfa)
    removed = [s for s in dfa.states if s not in reachable]
    pruned = DFA(
        states=[s for s in dfa.states if s in reachable],
        transitions={s: dict(dfa.transitions.get(s, {})) for s in reachable},
        start_state=dfa.start_state,
        accepting_states=set(dfa.accepting_states) & reachable,
        trap_state=dfa.trap_state,
    )
    return pruned, removed


def _partition_refinement(dfa: DFA) -> list[set[str]]:
    """
    Refine partitions until stable.

    Returns the final list of equivalence classes (each a set of states).
    """
    # Step 1: initial partition -> {accepting} vs {non-accepting}
    accepting = {s for s in dfa.states if s in dfa.accepting_states}
    non_accepting = {s for s in dfa.states if s not in dfa.accepting_states}
    partitions: list[set[str]] = [p for p in (accepting, non_accepting) if p]

    # Collect every symbol that appears anywhere in the transition table.
    symbols: set[str] = set()
    for row in dfa.transitions.values():
        symbols |= set(row.keys())

    changed = True
    while changed:
        changed = False
        new_partitions: list[set[str]] = []
        for block in partitions:
            # Group states inside this block by their signature.
            signature_map: dict[tuple[str, ...], set[str]] = {}
            for state in block:
                sig: list[str] = []
                for sym in sorted(symbols):
                    nxt = dfa.transitions.get(state, {}).get(sym, dfa.trap_state)
                    # Which partition index does `nxt` currently live in?
                    idx = -1
                    for i, part in enumerate(partitions):
                        if nxt in part:
                            idx = i
                            break
                    sig.append(str(idx))
                key = tuple(sig)
                signature_map.setdefault(key, set()).add(state)

            if len(signature_map) > 1:
                changed = True
            new_partitions.extend(signature_map.values())
        partitions = new_partitions

    return partitions


def minimize(dfa: DFA) -> tuple[DFA, dict[str, object]]:
    """
    Minimize `dfa`.

    Returns:
        (minimized_dfa, metadata)

        metadata contains:
            - "removed_unreachable": list of states pruned
            - "partitions": final partition list (each a set of states)
            - "state_count_before": int
            - "state_count_after": int
            - "merged_groups": list of sets of merged states
    """
    pruned, removed = _prune_unreachable(dfa)
    partitions = _partition_refinement(pruned)

    # Name each partition block by a canonical state name.
    # If a block contains exactly one original state, keep that name.
    # Otherwise, generate a new name like "M0", "M1", ...
    block_names: dict[int, str] = {}
    counter = 0
    merged_groups: list[set[str]] = []
    for i, block in enumerate(partitions):
        if len(block) == 1:
            block_names[i] = next(iter(block))
        else:
            block_names[i] = f"M{counter}"
            counter += 1
            merged_groups.append(block)

    def block_index(state: str) -> int:
        for i, block in enumerate(partitions):
            if state in block:
                return i
        return -1

    # Build the minimized transition table.
    min_transitions: dict[str, dict[str, str]] = {}
    for block in partitions:
        new_name = block_names[block_index(next(iter(block)))]
        row: dict[str, str] = {}
        sample = next(iter(block))
        for sym, nxt in pruned.transitions.get(sample, {}).items():
            row[sym] = block_names[block_index(nxt)]
        min_transitions[new_name] = row

    min_states = list(min_transitions.keys())
    min_start = block_names[block_index(pruned.start_state)]
    min_accepting = {
        block_names[block_index(s)]
        for s in pruned.accepting_states
    }
    min_trap = block_names[block_index(pruned.trap_state)]

    minimized = DFA(
        states=min_states,
        transitions=min_transitions,
        start_state=min_start,
        accepting_states=min_accepting,
        trap_state=min_trap,
    )

    metadata: dict[str, object] = {
        "removed_unreachable": removed,
        "partitions": [set(p) for p in partitions],
        "state_count_before": len(dfa.states),
        "state_count_after": len(min_states),
        "merged_groups": merged_groups,
    }
    return minimized, metadata