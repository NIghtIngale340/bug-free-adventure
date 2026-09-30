"""BE-007 edge-case suite for the Minimized DFA pipeline.

Categories mirror PROJECT_SPEC_EMPLOYEE_ID_VALIDATOR.md section 13.
Every test asserts the ValidationService result, which is the exact
same path the GUI uses.
"""

import pytest

from app.core.models import SimulationStatus
from app.services.validation_service import ValidationService


@pytest.fixture(scope="module")
def validator() -> ValidationService:
    return ValidationService()


# --- 1. Valid standard IDs --------------------------------------------------

@pytest.mark.parametrize(
    "s",
    [
        "EMP-2026-0001",
        "EMP-2026-0042",
        "EMP-2026-9999",
        "EMP-1999-5555",
        "EMP-2030-7777",
    ],
)
def test_valid_standard(validator: ValidationService, s: str) -> None:
    r = validator.validate(s)
    assert r.accepted is True
    assert r.status is SimulationStatus.ACCEPTED
    assert r.final_state == "q13"
    assert r.processed_symbols == 13
    assert r.total_symbols == 13


# --- 2. Boundary numeric values ---------------------------------------------

@pytest.mark.parametrize(
    "s",
    [
        "EMP-2000-0000",
        "EMP-2099-9999",
        "EMP-0000-0000",
        "EMP-9999-9999",
    ],
)
def test_valid_boundaries(validator: ValidationService, s: str) -> None:
    assert validator.validate(s).accepted is True


# --- 3. Invalid prefix ------------------------------------------------------

@pytest.mark.parametrize(
    "s",
    [
        "AXP-2026-0001",
        "EM-2026-0001",
        "EMPP-2026-0001",
        "emp-2026-0001",
        "Emp-2026-0001",
    ],
)
def test_invalid_prefix(validator: ValidationService, s: str) -> None:
    r = validator.validate(s)
    assert r.accepted is False
    assert r.status in {
        SimulationStatus.REJECTED_INVALID_SYMBOL,
        SimulationStatus.REJECTED_NO_TRANSITION,
        SimulationStatus.REJECTED_NON_FINAL_STATE,
    }


# --- 4. Wrong year length ---------------------------------------------------

@pytest.mark.parametrize(
    "s",
    [
        "EMP-26-0001",
        "EMP-20261-0001",
        "EMP-202-0001",
    ],
)
def test_wrong_year_length(validator: ValidationService, s: str) -> None:
    assert validator.validate(s).accepted is False


# --- 5. Wrong sequence length -----------------------------------------------

@pytest.mark.parametrize(
    "s",
    [
        "EMP-2026-1",
        "EMP-2026-12",
        "EMP-2026-123",
        "EMP-2026-00001",
        "EMP-2026-000001",
    ],
)
def test_wrong_sequence_length(validator: ValidationService, s: str) -> None:
    assert validator.validate(s).accepted is False


# --- 6. Missing separator ---------------------------------------------------

@pytest.mark.parametrize(
    "s",
    [
        "EMP2026-0001",
        "EMP-20260001",
        "EMP20260001",
    ],
)
def test_missing_separator(validator: ValidationService, s: str) -> None:
    assert validator.validate(s).accepted is False


# --- 7. Extra separator -----------------------------------------------------

@pytest.mark.parametrize(
    "s",
    [
        "EMP--2026-0001",
        "EMP-2026--0001",
        "EMP---2026---0001",
    ],
)
def test_extra_separator(validator: ValidationService, s: str) -> None:
    assert validator.validate(s).accepted is False


# --- 8. Invalid symbols -----------------------------------------------------

@pytest.mark.parametrize(
    "s, expected_idx",
    [
        ("EMP-2026-12A4", 11),
        ("EMP_2026_0001", 3),
        ("EMP-2026-00!1", 11),
        ("EMP-2026-00 1", 11),
        (" EMP-2026-0001", 0),
    ],
)
def test_invalid_symbol_position(
    validator: ValidationService, s: str, expected_idx: int
) -> None:
    r = validator.validate(s)
    assert r.accepted is False
    assert r.status is SimulationStatus.REJECTED_INVALID_SYMBOL
    assert r.error_position == expected_idx


# --- 9. Empty input ---------------------------------------------------------

def test_empty_input(validator: ValidationService) -> None:
    r = validator.validate("")
    assert r.accepted is False
    assert r.status is SimulationStatus.REJECTED_EMPTY_INPUT
    assert r.final_state is None
    assert r.trace == []
    assert r.processed_symbols == 0


# --- 10. Very long input ----------------------------------------------------

def test_very_long_input(validator: ValidationService) -> None:
    long_input = "EMP-2026-0042" + "0" * 500
    r = validator.validate(long_input)
    assert r.accepted is False
    # The trap happens at position 13 (first extra '0').
    assert r.error_position == 13


# --- 11. Multiple consecutive validations -----------------------------------

def test_multiple_validations_are_independent(
    validator: ValidationService,
) -> None:
    good = validator.validate("EMP-2026-0042")
    bad = validator.validate("EMP-2026-12A4")
    good_again = validator.validate("EMP-2026-0042")
    assert good.accepted is True
    assert bad.accepted is False
    assert good_again.accepted is True
    assert good.trace == good_again.trace


# --- 12. Trace length matches processed length for valid inputs -------------

def test_trace_length_matches_for_valid(
    validator: ValidationService,
) -> None:
    r = validator.validate("EMP-2026-0042")
    assert len(r.trace) == r.processed_symbols == 13
