"""DFA class contract + behaviour of the derived minimal DFA."""

import pytest

from app.core.dfa import DFA

VALID = ["EMP-2026-0001", "EMP-2026-0042", "EMP-2026-9999", "EMP-2000-0000", "EMP-2099-1234",
         "EMP-1999-5555", "EMP-0000-0000", "EMP-9999-9999"]
INVALID = ["EMP2026-0001", "EMP-26-0001", "EMP-2026-123", "emp-2026-0001", "EMP-2026-12A4",
           "EMP-2026-00001", "", "EMP-2026-0001-", "EMP--2026-0001", "EMP-2026-0001\n"]


@pytest.mark.parametrize("w", VALID)
def test_valid_ids_accepted(dfa: DFA, w: str) -> None:
    assert dfa.accepts(w) is True
    assert dfa.run(w) == "q13"


@pytest.mark.parametrize("w", INVALID)
def test_invalid_ids_rejected(dfa: DFA, w: str) -> None:
    assert dfa.accepts(w) is False


def test_delta_is_total(dfa: DFA) -> None:
    assert all(set(row) == set(dfa.alphabet) for row in dfa.transitions.values())


def test_dead_state_is_sticky_and_unique(dfa: DFA) -> None:
    assert dfa.dead_states == {"q_trap"}
    assert all(dfa.step("q_trap", a) == "q_trap" for a in dfa.alphabet)


def test_symbol_outside_sigma_has_no_transition(dfa: DFA) -> None:
    with pytest.raises(ValueError):
        dfa.step("q0", "A")


def test_expected_and_symbols_needed(dfa: DFA) -> None:
    assert dfa.expected("q0") == ["E"]
    assert dfa.expected("q4") == list("0123456789")
    assert dfa.expected("q13") == []
    assert [dfa.symbols_needed(f"q{i}") for i in range(14)] == list(range(13, -1, -1))
    assert dfa.symbols_needed("q_trap") is None


# --- constructor validation ---------------------------------------------------------

def _ok():
    return dict(states=["a", "b"], alphabet="x", transitions={"a": {"x": "b"}, "b": {"x": "b"}},
                start_state="a", accepting_states={"b"})


@pytest.mark.parametrize("patch, why", [
    ({"start_state": "zz"}, "start"),
    ({"accepting_states": {"zz"}}, "accepting"),
    ({"transitions": {"a": {"x": "zz"}, "b": {"x": "b"}}}, "target"),
    ({"transitions": {"a": {"x": "b"}}}, "total"),
    ({"states": ["a", "a"]}, "duplicate"),
])
def test_constructor_rejects_bad_automata(patch, why) -> None:
    with pytest.raises(ValueError):
        DFA(**{**_ok(), **patch})


def test_constructor_copies_its_inputs() -> None:
    args = _ok()
    d = DFA(**args)
    args["transitions"]["a"]["x"] = "a"
    assert d.step("a", "x") == "b"
