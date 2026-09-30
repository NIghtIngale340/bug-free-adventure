"""Offscreen GUI tests: call the slots directly (QtTest is not required)."""

import pytest

from app.data.test_cases import MASTER_TEST_SUITE


@pytest.fixture
def sim(window):
    return window.simulate


def test_loading_never_starts_the_run(sim) -> None:
    sim.load("EMP-2026-0042")
    assert not sim._timer.isActive()
    assert sim.history.rowCount() == 0 and sim.banner._title.text() == "READY"
    assert sim.diagram.view._visited == set() and sim.diagram.view._current == {"q0"}


@pytest.mark.parametrize("text", ["EMP-2026-0001 ", " EMP-2026-0001", "\tEMP-2026-0001"])
def test_input_is_never_trimmed_and_whitespace_is_rejected(sim, text) -> None:
    sim.input.setText(text)
    sim.load_from_input()
    assert sim._text == text
    assert sim.banner._title.text() == "REJECTED"
    assert "not in the alphabet Σ" in sim.banner._text.text()


def test_step_by_step_and_run_all_render_the_same_final_state(sim) -> None:
    sim.load("EMP-2026-0042")
    for _ in range(13):
        assert sim.step_forward()
    stepped = (sim.banner._title.text(), sim.formula.text(), sim.history.rowCount())
    sim.load("EMP-2026-0042")
    sim.run_all()
    assert stepped == (sim.banner._title.text(), sim.formula.text(), sim.history.rowCount()) == ("ACCEPTED", "δ(q12, 2) = q13", 13)


def test_diagram_marks_only_visited_states(sim) -> None:
    sim.load("EMP-2026-0042")
    for _ in range(6):
        sim.step_forward()
    view = sim.diagram.view
    assert view._visited == {f"q{i}" for i in range(6)} and view._current == {"q6"}
    assert not {f"q{i}" for i in range(7, 14)} & (view._visited | view._current)   # unvisited stay idle


def test_trap_run_highlights_the_dead_state_and_stops(sim) -> None:
    sim.load("EMP2026-0001")
    sim.run_all()
    assert sim.banner._title.text() == "REJECTED" and "expects '-' but read '2'" in sim.banner._text.text()
    assert sim.diagram.view._current == {"q_trap"} and sim.history.rowCount() == 4
    assert not sim.btn_step.isEnabled()


def test_previous_step_and_reset(sim) -> None:
    sim.load("EMP-2026-0042")
    for _ in range(5):
        sim.step_forward()
    sim.step_back()
    assert sim.history.rowCount() == 4 and sim.state_label.text().endswith("q3 → q4")
    sim.reset()
    assert sim.history.rowCount() == 0 and sim.btn_step.isEnabled()


def test_play_uses_the_timer_and_speed_maps_to_the_interval(sim) -> None:
    sim.load("EMP-2026-0042")
    sim.toggle_play()
    assert sim._timer.isActive() and sim._timer.interval() == 800 and sim.speed_label.text() == "1.0×"
    sim.speed.setValue(40)
    assert sim._timer.interval() == 200
    sim.toggle_play()
    assert not sim._timer.isActive()


@pytest.mark.parametrize("mode", ["DFA", "SUBSET", "NFA"])
def test_all_three_models_run_and_agree(sim, mode) -> None:
    sim.model.setCurrentIndex(sim.model.findData(mode))
    sim.load("EMP-2026-0042")
    sim.run_all()
    assert sim.banner._title.text() == "ACCEPTED"
    assert sim.diagram.view.graph.title.lower().startswith(("minimal", "dfa (subset", "ε-nfa"))


def test_empty_input_shows_a_clear_message(sim) -> None:
    sim.load("")
    assert sim.banner._title.text() == "REJECTED" and "Please enter an Employee ID" in sim.banner._text.text()
    assert not sim.btn_step.isEnabled() and sim.history.rowCount() == 0


def test_theory_tabs_are_computed_from_the_pipeline(window) -> None:
    th = window.theory
    assert [th.tabs.tabText(i) for i in range(th.tabs.count())][:3] == ["Language", "Regular expression", "ε-NFA"]
    assert "none — the DFA is already minimal" in th._min_summary.text() and "15 → 15" in th._min_summary.text()
    assert len(th._rounds) == 14 and th._round_label.text().startswith("Partition P13")


def test_last_run_is_painted_on_the_minimal_dfa_table(window) -> None:
    window.simulate.load("EMP2026-0001")
    window.simulate.run_all()
    t = window.theory._min_table
    assert t.item(3, window.theory._min_tab.col_of["2"]).background().color().name().upper() == "#341A1F"


def test_tests_page_runs_the_whole_suite_on_all_models(window) -> None:
    tp = window.tests
    n = len(MASTER_TEST_SUITE)
    assert f"{n} / {n} passed" in tp.stats.text() and f"agree on {n} / {n}" in tp.stats.text()


def test_batch_validation_uses_lines_exactly_as_written(window) -> None:
    tp = window.tests
    tp.batch_in.setPlainText("EMP-2026-0001\nEMP-2026-0001 \n\nEMP2026-0001")
    tp.run_batch()
    verdicts = [tp.batch_out.item(r, 2).text() for r in range(tp.batch_out.rowCount())]
    assert verdicts == ["ACCEPTED", "REJECTED", "REJECTED", "REJECTED"]


def test_tests_page_can_send_an_input_to_the_simulator(window) -> None:
    window.tests.simulateRequested.emit("EMP-2026-9999")
    assert window.stack.currentIndex() == 0 and window.simulate._text == "EMP-2026-9999"


def test_window_fits_the_minimum_size(window) -> None:
    window.resize(window.minimumSize())
    assert window.minimumWidth() <= 1040 and window.minimumHeight() <= 660
