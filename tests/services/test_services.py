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


def test_invalid_symbol_finishes_session_before_any_step() -> None:
    svc = SimulationService()
    sid = svc.create_session("EMP-2026-12A4")
    assert svc.is_finished(sid) and svc.step(sid) is None
    result = svc.result(sid)
    assert result.status is SimulationStatus.REJECTED_INVALID_SYMBOL and result.error_position == 11


def test_structural_failure_ends_the_session_in_the_trap() -> None:
    svc = SimulationService()
    sid = svc.create_session("EMP2026-0001")
    steps = []
    while (s := svc.step(sid)) is not None:
        steps.append(s)
    assert steps[-1].symbol == "2" and steps[-1].to_state == "q_trap"
    assert svc.is_finished(sid) and svc.active_states(sid) == {"q_trap"}


def test_sessions_are_bounded_and_closable() -> None:
    svc = SimulationService()
    first = svc.create_session("EMP-2026-0042")
    for _ in range(40):
        svc.create_session("E")
    assert svc.step(first) is None            # evicted
    sid = svc.create_session("EMP-2026-0042")
    svc.close(sid)
    assert svc.step(sid) is None


# --- Metadata ---------------------------------------------------------------

def test_metadata_shape() -> None:
    svc = SimulationService()
    meta = svc.get_metadata()
    assert meta.start_state == "q0"
    assert meta.accepting_states == ["q13"]
    assert len(meta.alphabet) == 14
    assert "q_trap" in meta.states
    assert meta.re_pattern == "EMP-D⁴-D⁴"


def test_metadata_transition_table_has_q0_entry() -> None:
    svc = SimulationService()
    meta = svc.get_metadata()
    row = meta.transition_table["q0"]
    assert row["E"] == "q1" and {a for a, t in row.items() if t != "q_trap"} == {"E"}


def test_simulation_service_nfa_mode_stepping() -> None:
    svc = SimulationService()
    sid = svc.create_session("EMP-2026-0042", mode="NFA")
    step1 = svc.step(sid)
    assert step1 is not None
    assert step1.from_state == "{n0}"
    assert step1.to_state == "{n1, n2}"
    res = svc.run_all(sid)
    assert res.accepted is True
    assert res.final_state == "{n25}"


def test_subset_mode_runs_the_unminimized_dfa() -> None:
    svc = SimulationService()
    sid = svc.create_session("EMP-2026-0042", mode="SUBSET")
    assert svc.step(sid).from_state == "D0"
    assert svc.run_all(sid).final_state == "D13"


def test_metadata_includes_nfa_summary() -> None:
    svc = SimulationService()
    meta = svc.get_metadata()
    assert meta.nfa_summary is not None
    assert meta.nfa_summary["start_state"] == "n0"
    assert meta.nfa_summary["accepting_states"] == ["n25"]
    assert meta.nfa_summary["epsilon_edges"] == 12
    assert len(meta.nfa_summary["subset_trace"]) == 14


def test_metadata_numbers_are_computed_not_typed(pipeline) -> None:
    ms = SimulationService().get_metadata().minimization_summary
    assert ms["unminimized_states"] == len(pipeline.subset_dfa.states) == 15
    assert ms["minimized_states"] == len(pipeline.min_dfa.states) == 15
    assert ms["merged_groups"] == [] and ms["rounds"] == 13


def test_metadata_transition_table_is_total() -> None:
    meta = SimulationService().get_metadata()
    assert all(set(row) == set(meta.alphabet) for row in meta.transition_table.values())
