"""Unit tests for BE-006: ValidationService and SimulationService."""


from app.core.models import SimulationStatus
from app.services.simulation_service import SimulationService
from app.services.validation_service import ValidationService

# --- ValidationService ------------------------------------------------------

def test_validation_service_accepts_valid() -> None:
    svc = ValidationService()
    result = svc.validate("EMP-2026-0042")
    assert result.accepted is True
    assert result.status is SimulationStatus.ACCEPTED
    assert result.final_state == "q13"


def test_validation_service_rejects_invalid() -> None:
    svc = ValidationService()
    result = svc.validate("EMP-2026-12A4")
    assert result.accepted is False
    assert result.status is SimulationStatus.REJECTED_INVALID_SYMBOL


def test_validation_service_empty() -> None:
    svc = ValidationService()
    result = svc.validate("")
    assert result.status is SimulationStatus.REJECTED_EMPTY_INPUT


# --- SimulationService: sessions -------------------------------------------

def test_create_session_returns_id() -> None:
    svc = SimulationService()
    sid = svc.create_session("EMP-2026-0042")
    assert isinstance(sid, str)
    assert len(sid) > 0


def test_step_returns_transition_step() -> None:
    svc = SimulationService()
    sid = svc.create_session("EMP-2026-0042")
    step1 = svc.step(sid)
    assert step1 is not None
    assert step1.step == 1
    assert step1.symbol == "E"
    assert step1.from_state == "q0"
    assert step1.to_state == "q1"
    assert step1.is_valid is True


def test_step_sequence_matches_input_length() -> None:
    svc = SimulationService()
    sid = svc.create_session("EMP-2026-0042")
    steps = []
    while True:
        s = svc.step(sid)
        if s is None:
            break
        steps.append(s)
    assert len(steps) == 13
    assert steps[-1].to_state == "q13"


def test_run_all_returns_full_result() -> None:
    svc = SimulationService()
    sid = svc.create_session("EMP-2026-0042")
    result = svc.run_all(sid)
    assert result.accepted is True
    assert result.status is SimulationStatus.ACCEPTED


def test_run_all_after_partial_stepping() -> None:
    svc = SimulationService()
    sid = svc.create_session("EMP-2026-0042")
    svc.step(sid)
    svc.step(sid)
    result = svc.run_all(sid)
    assert result.accepted is True


def test_reset_returns_to_start_state() -> None:
    svc = SimulationService()
    sid = svc.create_session("EMP-2026-0042")
    svc.step(sid)
    svc.step(sid)
    svc.reset(sid)
    step1 = svc.step(sid)
    assert step1 is not None
    assert step1.from_state == "q0"
    assert step1.symbol == "E"


def test_step_returns_none_after_finish() -> None:
    svc = SimulationService()
    sid = svc.create_session("EMP-2026-0042")
    svc.run_all(sid)
    assert svc.step(sid) is None


def test_step_on_empty_input_finishes_immediately() -> None:
    svc = SimulationService()
    sid = svc.create_session("")
    assert svc.step(sid) is None


def test_invalid_symbol_finishes_session() -> None:
    svc = SimulationService()
    sid = svc.create_session("EMP-2026-12A4")
    last = None
    while True:
        s = svc.step(sid)
        if s is None:
            break
        last = s
    assert last is not None
    assert last.symbol == "A"
    assert last.to_state == "q_trap"


# --- Metadata ---------------------------------------------------------------

def test_metadata_shape() -> None:
    svc = SimulationService()
    meta = svc.get_metadata()
    assert meta.start_state == "q0"
    assert meta.accepting_states == ["q13"]
    assert len(meta.alphabet) == 14
    assert "q_trap" in meta.states
    assert meta.re_pattern.startswith("^EMP-")


def test_metadata_transition_table_has_q0_entry() -> None:
    svc = SimulationService()
    meta = svc.get_metadata()
    assert meta.transition_table["q0"] == {"E": "q1"}


def test_simulation_service_nfa_mode_stepping() -> None:
    svc = SimulationService()
    sid = svc.create_session("EMP-2026-0042", mode="NFA")
    step1 = svc.step(sid)
    assert step1 is not None
    assert step1.from_state == "{q0}"
    assert step1.to_state == "{q1}"
    res = svc.run_all(sid)
    assert res.accepted is True
    assert res.final_state == "{q13}"


def test_metadata_includes_nfa_summary() -> None:
    svc = SimulationService()
    meta = svc.get_metadata()
    assert meta.nfa_summary is not None
    assert meta.nfa_summary["start_state"] == "q0"
    assert meta.nfa_summary["accepting_states"] == ["q13"]
    assert len(meta.nfa_summary["subset_trace"]) > 0