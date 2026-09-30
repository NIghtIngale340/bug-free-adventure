"""Run engine: Layer 1 (alphabet) + Layer 2 (automaton) + result construction."""

import pytest

from app.core.models import SimulationStatus as S
from app.core.simulator import Run, simulate, simulate_nfa
from app.data.test_cases import MASTER_TEST_SUITE


@pytest.mark.parametrize("w", ["EMP-2026-0001", "EMP-2026-0042", "EMP-2026-9999", "EMP-2000-0000"])
def test_valid_ids_accepted(w: str) -> None:
    r = simulate(w)
    assert (r.accepted, r.status, r.final_state) == (True, S.ACCEPTED, "q13")
    assert r.processed_symbols == r.total_symbols == len(r.trace) == 13
    assert r.error_message is None and r.error_position is None


def test_empty_input() -> None:
    r = simulate("")
    assert r.status is S.REJECTED_EMPTY_INPUT and r.final_state is None and r.trace == []
    assert r.processed_symbols == 0


# --- Layer 1: alphabet -----------------------------------------------------------------

def test_invalid_symbol_rejects_before_the_automaton_runs() -> None:
    r = simulate("EMP-2026-12A4")
    assert r.status is S.REJECTED_INVALID_SYMBOL
    assert r.error_position == 11 and r.trace == [] and r.final_state is None
    assert r.processed_symbols == 0 and r.total_symbols == 13
    assert "'A' at position 11" in r.explanation


def test_layer1_checks_the_whole_string_first_and_lists_every_offender() -> None:
    # structurally wrong at index 3 AND contains '!': the alphabet violation wins and is complete
    r = simulate("EMP2026-00!1 ?")
    assert r.status is S.REJECTED_INVALID_SYMBOL and r.error_position == 10
    assert "'!' at position 10" in r.explanation and "'?' at position 13" in r.explanation


def test_lowercase_prefix_is_invalid_symbol() -> None:
    r = simulate("emp-2026-0001")
    assert r.status is S.REJECTED_INVALID_SYMBOL and r.error_position == 0


# --- Layer 2: structure ------------------------------------------------------------------

@pytest.mark.parametrize("w, pos, expects", [
    ("EMP2026-0001", 3, "expects '-' but read '2'"),
    ("EMP-26-0001", 6, "expects a digit 0–9 but read '-'"),
    ("EMP-2026-00001", 13, "expects end of input but read '1'"),
    ("PMP-2026-0001", 0, "expects 'E' but read 'P'"),
])
def test_structural_rejection_says_what_was_expected(w, pos, expects) -> None:
    r = simulate(w)
    assert r.status is S.REJECTED_NO_TRANSITION and r.final_state == "q_trap"
    assert r.error_position == pos and expects in r.explanation
    assert r.trace[-1].is_valid is False and r.trace[-1].to_state == "q_trap"
    assert len(r.trace) == pos + 1                      # the run stops at the dead state


def test_too_short_input_reports_how_much_is_missing() -> None:
    r = simulate("EMP-2026-123")
    assert r.status is S.REJECTED_NON_FINAL_STATE and r.final_state == "q12"
    assert "1 more symbol" in r.explanation and "digit 0–9" in r.explanation
    assert simulate("EMP-2026-1").explanation.count("3 more")


# --- trace shape ---------------------------------------------------------------------------

def test_trace_steps_are_sequential_and_chained() -> None:
    t = simulate("EMP-2026-0042").trace
    assert [s.step for s in t] == list(range(1, 14))
    assert t[0].from_state == "q0" and t[0].to_state == "q1" and t[0].is_valid
    assert all(a.to_state == b.from_state for a, b in zip(t, t[1:]))


# --- NFA / subset-DFA modes ---------------------------------------------------------------------

def test_nfa_run_shows_subsets_with_epsilon_closure() -> None:
    r = simulate_nfa("EMP-2026-0042")
    assert r.accepted and r.final_state == "{n25}"
    assert r.trace[0].from_state == "{n0}" and r.trace[0].to_state == "{n1, n2}"


def test_nfa_dead_end_is_the_empty_set() -> None:
    r = simulate_nfa("PMP-2026-0001")
    assert r.status is S.REJECTED_NO_TRANSITION and r.final_state == "∅"
    assert r.trace[-1].to_state == "∅"


# --- one engine: stepping == one-shot ----------------------------------------------------------

@pytest.mark.parametrize("mode", ["DFA", "SUBSET", "NFA"])
def test_step_by_step_equals_one_shot_on_the_whole_suite(pipeline, mode) -> None:
    machine = {"DFA": pipeline.min_dfa, "SUBSET": pipeline.subset_dfa, "NFA": pipeline.nfa}[mode]
    for tc in MASTER_TEST_SUITE:
        run, steps = Run(tc.input_str, machine), []
        while (s := run.step()) is not None:
            steps.append(s)
        assert steps == run.result().trace == simulate(tc.input_str, machine).trace
        assert run.result().accepted == tc.expected_accepted
