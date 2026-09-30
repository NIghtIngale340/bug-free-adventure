"""
INTEGRATION TEST SUITE: Master Test Cases Compliance
Verifies all 28 categorized test cases against the real Minimized DFA simulator.
"""

import pytest

from app.data.test_cases import MASTER_TEST_SUITE, TestCase
from app.services.simulation_service import SimulationService
from app.services.validation_service import ValidationService


@pytest.fixture
def val_service():
    return ValidationService()


@pytest.fixture
def sim_service():
    return SimulationService()


@pytest.mark.parametrize("tc", MASTER_TEST_SUITE, ids=lambda tc: tc.id)
def test_all_master_test_cases_validation_service(val_service, tc: TestCase):
    """Ensure ValidationService evaluates all 28 test cases accurately."""
    res = val_service.validate(tc.input_str)
    assert res.accepted == tc.expected_accepted, (
        f"Validation failed for {tc.id} ({tc.input_str!r}): "
        f"Expected {tc.expected_accepted}, got {res.accepted}. "
        f"Explanation: {res.explanation}"
    )


@pytest.mark.parametrize("tc", MASTER_TEST_SUITE, ids=lambda tc: tc.id)
def test_all_master_test_cases_simulation_service(sim_service, tc: TestCase):
    """Ensure SimulationService.validate evaluates all 28 test cases accurately."""
    res = sim_service.validate(tc.input_str)
    assert res.accepted == tc.expected_accepted, (
        f"Simulation failed for {tc.id} ({tc.input_str!r}): "
        f"Expected {tc.expected_accepted}, got {res.accepted}. "
        f"Explanation: {res.explanation}"
    )
