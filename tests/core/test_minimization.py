"""Unit tests for BE-004: DFA minimization."""

from app.core.dfa import DFA
from app.core.minimizer import minimize


def test_minimize_returns_dfa_and_metadata() -> None:
    dfa = DFA()
    minimized, meta = minimize(dfa)
    assert isinstance(minimized, DFA)
    assert "state_count_before" in meta
    assert "state_count_after" in meta


def test_minimize_preserves_acceptance() -> None:
    dfa = DFA()
    minimized, _ = minimize(dfa)

    samples = [
        "EMP-2026-0001",
        "EMP-2026-0042",
        "EMP-2026-9999",
        "EMP-2000-0000",
        "EMP2099-1234",
        "emp-2026-0001",
        "EMP-2026-12A4",
        "",
    ]
    for s in samples:
        assert dfa.accepts(s) == minimized.accepts(s), f"mismatch on {s!r}"


def test_canonical_dfa_is_already_minimal() -> None:
    """
    Per AUTOMATA_THEORY_BASELINE.md, the canonical DFA is already minimal.
    State count should not shrink.
    """
    dfa = DFA()
    minimized, meta = minimize(dfa)
    assert meta["state_count_before"] == meta["state_count_after"]


def test_unreachable_states_removed() -> None:
    # Build a DFA with an extra unreachable state.
    transitions = dict(DFA().transitions)
    transitions["q_unreachable"] = {"E": "q1"}
    dfa = DFA(
        states=list(transitions.keys()),
        transitions=transitions,
        start_state="q0",
        accepting_states={"q13"},
        trap_state="q_trap",
    )
    minimized, meta = minimize(dfa)
    assert "q_unreachable" in meta["removed_unreachable"]
    assert "q_unreachable" not in minimized.states