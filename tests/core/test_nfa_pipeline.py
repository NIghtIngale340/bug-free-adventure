"""RE -> epsilon-NFA (Thompson) -> DFA (subset construction)."""

import pytest

from app.core.nfa import NFA, epsilon_closure, move, subset_construction, thompson
from app.core.regex import Class, Concat, Lit, Repeat, alphabet_of, expanded, formal, length_of
from app.core.simulator import simulate_nfa
from app.data.id_rules import ALPHABET, ID_REGEX, TOTAL_LENGTH


def test_regex_notation_and_derived_facts() -> None:
    assert formal(ID_REGEX) == "EMP-D⁴-D⁴"
    assert expanded(ID_REGEX) == "E·M·P·-·D·D·D·D·-·D·D·D·D"
    assert TOTAL_LENGTH == 13 == length_of(ID_REGEX)
    assert ALPHABET == alphabet_of(ID_REGEX) == set("EMP-0123456789")


def test_thompson_structure(pipeline) -> None:
    nfa = pipeline.nfa
    assert len(nfa.states) == 26                # 13 atoms x 2 states
    assert nfa.epsilon_edge_count == 12         # 12 joins between 13 atoms
    assert nfa.start_state == "n0" and nfa.accepting_states == {"n25"}
    assert nfa.alphabet == ALPHABET
    assert not any("q_trap" in s for s in nfa.states)   # an NFA has no trap state


def test_epsilon_closure_and_move_really_used() -> None:
    nfa = thompson(ID_REGEX)
    after_e = move(nfa, epsilon_closure(nfa, {"n0"}), "E")
    assert after_e == {"n1"}                                    # move alone stops before the ε edge
    assert epsilon_closure(nfa, after_e) == {"n1", "n2"}        # closure follows n1 -ε-> n2
    assert nfa.step({"n0"}, "M") == frozenset()                 # no move -> empty set


def test_epsilon_closure_is_transitive() -> None:
    n = NFA(["a", "b", "c", "d"], {"c": {"x": {"d"}}}, "a", {"d"}, {"a": {"b"}, "b": {"c"}})
    assert epsilon_closure(n, {"a"}) == {"a", "b", "c"}
    assert n.accepts("x") and not n.accepts("") and not n.accepts("xx")


def test_genuine_nondeterminism_is_converted() -> None:
    # (a|a)b style: two a-moves from the start -> subset {p, q}
    n = NFA(["s", "p", "q", "f"], {"s": {"a": {"p", "q"}}, "p": {"b": {"f"}}, "q": {"b": {"f"}}},
            "s", {"f"})
    dfa, steps = subset_construction(n)
    assert any(len(st.subset) == 2 for st in steps)
    assert all(dfa.accepts(w) == n.accepts(w) for w in ["ab", "a", "b", "", "abb", "aab"])


def test_subset_construction_of_the_id_nfa(pipeline) -> None:
    dfa, steps = pipeline.subset_dfa, pipeline.subset_steps
    assert dfa.states == [f"D{i}" for i in range(14)] + ["D_trap"]
    assert steps[0].name == "D0" and steps[0].subset == {"n0"}
    assert steps[1].subset == {"n1", "n2"}                       # ε-closure visible in the subset
    assert [s.name for s in steps if s.accepting] == ["D13"]
    assert dfa.dead_states == {"D_trap"} and dfa.start_state == "D0"
    # every step lists a move for every symbol of Sigma exactly once
    for st in steps:
        assert sorted(a for m in st.moves for a in m.symbols) == sorted(ALPHABET)


@pytest.mark.parametrize("w", ["EMP-2026-0042", "EMP2026-0001", "EMP-2026-123", "EMP-2026-12A4", ""])
def test_nfa_simulation_agrees_with_dfa(pipeline, w: str) -> None:
    assert simulate_nfa(w).accepted == pipeline.subset_dfa.accepts(w) == pipeline.min_dfa.accepts(w)


def test_repeat_and_class_building_blocks() -> None:
    n = thompson(Concat((Lit("a"), Repeat(Class(("0", "1")), 2))))
    assert n.accepts("a01") and n.accepts("a11") and not n.accepts("a1") and not n.accepts("b01")


def test_re_segments_partition_the_input_and_match_the_regex() -> None:
    from app.data.id_rules import ID_SEGMENTS
    assert [(s.name, s.formal, s.start, s.end) for s in ID_SEGMENTS] == [
        ("prefix", "EMP", 0, 3), ("separator", "-", 3, 4), ("year YYYY", "D⁴", 4, 8),
        ("separator", "-", 8, 9), ("number NNNN", "D⁴", 9, 13)]
    assert ID_SEGMENTS[0].start == 0 and ID_SEGMENTS[-1].end == TOTAL_LENGTH
    assert all(a.end == b.start for a, b in zip(ID_SEGMENTS, ID_SEGMENTS[1:]))


def test_graph_explanations_are_derived_from_the_automata(pipeline) -> None:
    from app.core.present import pipeline_graphs
    g = pipeline_graphs(pipeline)
    tips = {n.name: n.tip for n in g["DFA"].nodes}
    assert "Expects '-' next" in tips["q3"] and "10 more" in tips["q3"]
    assert "start state" in tips["q0"] and "accepting state" in tips["q13"] and "dead state" in tips["q_trap"]
    assert "NFA subset {n5, n6}" in {n.name: n.tip for n in g["SUBSET"].nodes}["D3"]
    assert any(e.tip.startswith("ε-move n1 → n2") for e in g["NFA"].edges)
    assert all(e.tip and e.tip.startswith("δ(") or e.epsilon for k in g for e in g[k].edges)
