"""Unit tests for BE-003: DFA + subset construction."""

import pytest

from app.core.dfa import DFA
from app.core.nfa import canonical_nfa, subset_construction


@pytest.fixture
def dfa() -> DFA:
    return DFA()


# --- Canonical DFA correctness ---------------------------------------------

@pytest.mark.parametrize(
    "input_str",
    [
        "EMP-2026-0001",
        "EMP-2026-0042",
        "EMP-2026-9999",
        "EMP-2000-0000",
        "EMP-2099-1234",
        "EMP-1999-5555",
    ],
)
def test_valid_ids_accepted(dfa: DFA, input_str: str) -> None:
    assert dfa.accepts(input_str) is True


@pytest.mark.parametrize(
    "input_str",
    [
        "EMP2026-0001",   # missing first hyphen
        "EMP-26-0001",    # year too short
        "EMP-2026-123",   # sequence too short
        "emp-2026-0001",  # lowercase
        "EMP-2026-12A4",  # invalid symbol
        "EMP-2026-00001", # sequence too long
        "",               # empty
    ],
)
def test_invalid_ids_rejected(dfa: DFA, input_str: str) -> None:
    assert dfa.accepts(input_str) is False


def test_trap_state_is_sticky(dfa: DFA) -> None:
    state = dfa.step("q0", "X")  # invalid first symbol
    assert state == dfa.trap_state
    assert dfa.step(state, "E") == dfa.trap_state
    assert dfa.step(state, "-") == dfa.trap_state


def test_trace_matches_canonical_path(dfa: DFA) -> None:
    state = dfa.start_state
    expected = ["q1", "q2", "q3", "q4"]
    for sym, want in zip("EMP-", expected):
        state = dfa.step(state, sym)
        assert state == want


# --- Subset construction ----------------------------------------------------

def test_subset_construction_produces_dfa() -> None:
    nfa = canonical_nfa()
    dfa, trace = subset_construction(nfa)
    assert isinstance(dfa, DFA)
    assert trace[0][0] == "D0"
    assert dfa.start_state == "D0"


def test_subset_construction_agrees_with_canonical() -> None:
    nfa = canonical_nfa()
    converted, _ = subset_construction(nfa)
    canonical = DFA()
    samples = [
        "EMP-2026-0001",
        "EMP-2026-12A4",
        "EMP2026-0001",
        "EMP-2026-9999",
        "",
    ]
    for s in samples:
        assert converted.accepts(s) == canonical.accepts(s)


def test_simulate_nfa_valid_input() -> None:
    from app.core.nfa import simulate_nfa
    res = simulate_nfa("EMP-2026-0042")
    assert res.accepted is True
    assert res.status.name == "ACCEPTED"
    assert res.final_state == "{q13}"
    assert len(res.trace) == 13
    assert res.trace[0].from_state == "{q0}"
    assert res.trace[0].to_state == "{q1}"


def test_simulate_nfa_invalid_symbol() -> None:
    from app.core.nfa import simulate_nfa
    res = simulate_nfa("EMP-2026-12A4")
    assert res.accepted is False
    assert res.status.name == "REJECTED_INVALID_SYMBOL"
    assert res.final_state == "∅"


def test_simulate_nfa_mismatch_transition() -> None:
    from app.core.nfa import simulate_nfa
    res = simulate_nfa("PMP-2026-0042")
    assert res.accepted is False
    assert res.status.name == "REJECTED_NO_TRANSITION"
    assert res.final_state == "∅"