"""Smoke tests for BE-002: frozen shared contracts."""

import pytest

from app.core.models import (
    AutomataMetadata,
    SimulationResult,
    SimulationStatus,
    TransitionStep,
)


def test_transition_step_is_frozen() -> None:
    from dataclasses import FrozenInstanceError

    step = TransitionStep(1, "E", "q0", "q1", True, "prefix E")
    assert step.symbol == "E"
    with pytest.raises(FrozenInstanceError):
        step.symbol = "M"  # type: ignore[misc]


def test_simulation_result_construction() -> None:
    result = SimulationResult(
        input_string="EMP-2026-0042",
        accepted=True,
        status=SimulationStatus.ACCEPTED,
        final_state="q13",
        trace=[],
        error_message=None,
        error_position=None,
        processed_symbols=13,
        total_symbols=13,
        explanation="OK",
    )
    assert result.accepted is True
    assert result.status is SimulationStatus.ACCEPTED


def test_automata_metadata_construction() -> None:
    meta = AutomataMetadata(
        states=["q0", "q13"],
        alphabet=["E", "M", "P", "-"] + [str(d) for d in range(10)],
        start_state="q0",
        accepting_states=["q13"],
        transition_table={"q0": {"E": "q1"}},
        re_pattern=r"^EMP-[0-9]{4}-[0-9]{4}$",
        minimization_summary={"states": 15},
    )
    assert meta.start_state == "q0"
    assert meta.accepting_states == ["q13"]