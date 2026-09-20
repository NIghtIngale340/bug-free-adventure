"""Unit tests for BE-005: Minimized DFA simulator & trace engine."""

import pytest

from app.core.models import SimulationStatus
from app.core.simulator import simulate

# --- Accepted cases ---------------------------------------------------------

@pytest.mark.parametrize(
    "input_str",
    [
        "EMP-2026-0001",
        "EMP-2026-0042",
        "EMP-2026-9999",
        "EMP-2000-0000",
        "EMP-2099-1234",
    ],
)
def test_valid_ids_accepted(input_str: str) -> None:
    result = simulate(input_str)
    assert result.accepted is True
    assert result.status is SimulationStatus.ACCEPTED
    assert result.final_state == "q13"
    assert result.processed_symbols == 13
    assert result.total_symbols == 13
    assert len(result.trace) == 13


# --- Empty input ------------------------------------------------------------

def test_empty_input_rejected() -> None:
    result = simulate("")
    assert result.accepted is False
    assert result.status is SimulationStatus.REJECTED_EMPTY_INPUT
    assert result.final_state is None
    assert result.trace == []
    assert result.processed_symbols == 0


# --- Invalid symbol ---------------------------------------------------------

def test_invalid_symbol_short_circuits() -> None:
    # 'A' at index 11 is outside Σ.
    result = simulate("EMP-2026-12A4")
    assert result.accepted is False
    assert result.status is SimulationStatus.REJECTED_INVALID_SYMBOL
    assert result.error_position == 11
    assert result.trace[-1].symbol == "A"
    assert result.trace[-1].to_state == "q_trap"


def test_lowercase_prefix_is_invalid_symbol() -> None:
    result = simulate("emp-2026-0001")
    assert result.status is SimulationStatus.REJECTED_INVALID_SYMBOL
    assert result.error_position == 0


# --- Structural rejection (valid alphabet, wrong structure) -----------------

@pytest.mark.parametrize(
    "input_str",
    [
        "EMP2026-0001",    # missing hyphen
        "EMP-26-0001",     # year too short
        "EMP-2026-123",    # sequence too short
        "EMP-2026-00001",  # sequence too long
    ],
)
def test_structural_rejection(input_str: str) -> None:
    result = simulate(input_str)
    assert result.accepted is False
    # Either trapped or ended in non-accepting state.
    assert result.status in {
        SimulationStatus.REJECTED_NO_TRANSITION,
        SimulationStatus.REJECTED_NON_FINAL_STATE,
    }


# --- Trace shape ------------------------------------------------------------

def test_trace_step_numbers_are_sequential() -> None:
    result = simulate("EMP-2026-0042")
    for i, step in enumerate(result.trace, start=1):
        assert step.step == i


def test_trace_first_step_matches_canonical() -> None:
    result = simulate("EMP-2026-0042")
    first = result.trace[0]
    assert first.symbol == "E"
    assert first.from_state == "q0"
    assert first.to_state == "q1"
    assert first.is_valid is True


def test_trap_is_sticky_in_result() -> None:
    # Missing hyphen -> trap early.
    result = simulate("EMP2026-0001")
    # Once we hit trap, we stop; verify final state is trap.
    assert result.final_state == "q_trap"
    assert result.accepted is False