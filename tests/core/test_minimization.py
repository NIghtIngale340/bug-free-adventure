"""DFA minimization (Moore partition refinement) incl. real merging."""

import itertools

from app.core.dfa import DFA
from app.core.equivalence import dfa_equivalent
from app.core.minimizer import minimize


def _redundant() -> DFA:
    # words over {a,b} ending in 'a'; A~C and B~D are equivalent, plus an unreachable state U.
    t = {"A": {"a": "B", "b": "C"}, "B": {"a": "B", "b": "C"}, "C": {"a": "D", "b": "C"},
         "D": {"a": "D", "b": "C"}, "U": {"a": "A", "b": "A"}}
    return DFA(list(t), "ab", t, "A", {"B", "D"})


def test_real_merging_and_unreachable_removal() -> None:
    r = minimize(_redundant())
    assert r.removed_unreachable == ("U",)
    assert sorted(map(tuple, map(sorted, r.merged_groups))) == [("A", "C"), ("B", "D")]
    assert (r.states_before, r.states_after) == (5, 2)
    assert r.state_map["A"] == r.state_map["C"] != r.state_map["B"]


def test_minimized_redundant_dfa_keeps_the_language() -> None:
    orig, r = _redundant(), minimize(_redundant())
    assert dfa_equivalent(orig, r.dfa).equal
    assert all(orig.accepts("".join(w)) == r.dfa.accepts("".join(w))
               for n in range(9) for w in itertools.product("ab", repeat=n))


def test_id_dfa_is_already_minimal_and_nothing_merges(pipeline) -> None:
    r = pipeline.minimization
    assert (r.states_before, r.states_after) == (15, 15)
    assert r.merged_groups == () and r.removed_unreachable == ()
    assert len(r.dfa.states) == len(set(r.state_map.values())) == 15


def test_refinement_rounds_are_recorded_and_isolate_one_state_per_round(pipeline) -> None:
    rounds = pipeline.minimization.rounds
    assert len(rounds) - 1 == 13                                   # P0 .. P13
    assert [len(p) for p in rounds] == [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]
    assert ("D13",) in rounds[0] and len(rounds[0]) == 2           # P0 = {F, Q\F}
    assert all(len(b) == 1 for b in rounds[-1])                    # final: all singletons
    for earlier, later in zip(rounds, rounds[1:]):                 # each round refines the last
        assert all(any(set(b) <= set(a) for a in earlier) for b in later)


def test_length_distinguishability_proof_is_computed(pipeline) -> None:
    d = pipeline.min_dfa
    needed = [d.symbols_needed(s) for s in d.states if not d.is_dead(s)]
    assert needed == list(range(13, -1, -1)) and len(set(needed)) == 14


def test_minimized_names_and_shape(pipeline) -> None:
    d = pipeline.min_dfa
    assert d.states == [f"q{i}" for i in range(14)] + ["q_trap"]
    assert d.start_state == "q0" and d.accepting_states == {"q13"}


def test_minimize_is_idempotent(pipeline) -> None:
    again = minimize(pipeline.min_dfa)
    assert again.merged_groups == () and again.dfa.transition_table() == pipeline.min_dfa.transition_table()
