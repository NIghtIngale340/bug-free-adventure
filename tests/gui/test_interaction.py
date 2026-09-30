"""Animation, hover / click explanations, RE-segment colouring, accessibility, fonts."""

import pytest
from PySide6.QtCore import QEventLoop, Qt, QTimer
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QApplication, QWidget

from app.data.id_rules import ID_SEGMENTS
from app.gui import theme
from app.gui.theme import PALETTE as P
from app.gui.widgets import automaton_diagram as ad
from app.gui.widgets.tape_view import TapeView, segment_legend


@pytest.fixture
def sim(window):
    return window.simulate


def _wait(ms: int) -> None:
    loop = QEventLoop()
    QTimer.singleShot(ms, loop.quit)
    loop.exec()


def _fill(view, name: str) -> str:
    return view._nodes[name][0].brush().color().name().lower()


# --- animation -------------------------------------------------------------------------------------

def test_state_colours_ease_towards_the_target(sim) -> None:
    view = sim.diagram.view
    sim.load("EMP-2026-0042")
    sim.step_forward()
    assert view._anim is not None and view._anim.state().name == "Running"    # transition in flight
    _wait(ad.DURATION_MS + 150)
    assert _fill(view, "q1") == QColor(P["accent"]).name().lower()            # current = solid amber
    assert _fill(view, "q0") == QColor(P["accent_bg"]).name().lower()         # left state = visited tint
    assert _fill(view, "q5") == QColor(P["surface"]).name().lower()           # untouched = idle


def test_reduced_motion_snaps_immediately(sim, monkeypatch) -> None:
    monkeypatch.setattr(ad, "ANIMATE", False)
    view = sim.diagram.view
    sim.load("EMP-2026-0042")
    sim.step_forward()
    assert view._anim is None and _fill(view, "q1") == QColor(P["accent"]).name().lower()


def test_retargeting_mid_animation_never_leaves_stale_colours(sim) -> None:
    view = sim.diagram.view
    sim.load("EMP-2026-0042")
    for _ in range(5):                       # five steps faster than the animation
        sim.step_forward()
    _wait(ad.DURATION_MS + 150)
    assert _fill(view, "q5") == QColor(P["accent"]).name().lower()
    assert all(_fill(view, f"q{i}") == QColor(P["accent_bg"]).name().lower() for i in range(5))


# --- hover / click explanations -----------------------------------------------------------------------

class _Ev:
    def accept(self) -> None: ...


def _hot(view, prefix: str, kind):
    return next(i for i in view._scene.items() if isinstance(i, kind) and i.tip.startswith(prefix))


def test_hovering_a_state_explains_it(sim) -> None:
    panel, view = sim.diagram, sim.diagram.view
    node = _hot(view, "q3", ad._HotEllipse)
    node.hoverEnterEvent(_Ev())
    assert "Expects '-' next" in panel.info.text() and "10 more" in panel.info.text()
    node.hoverLeaveEvent(_Ev())
    assert panel.info.text() == panel.DEFAULT


def test_clicking_a_transition_pins_its_explanation(sim) -> None:
    panel, view = sim.diagram, sim.diagram.view
    edge = _hot(view, "δ(q3", ad._HotPath)
    edge.mousePressEvent(_Ev())
    edge.hoverLeaveEvent(_Ev())
    assert panel.info.text().startswith("δ(q3, -) = q4")          # still shown after the mouse left
    _hot(view, "q13", ad._HotEllipse).hoverEnterEvent(_Ev())
    assert "accepting state" in panel.info.text()                  # hover temporarily overrides the pin


def test_dead_state_and_the_taken_dead_edge_are_explained(sim) -> None:
    sim.load("EMP2026-0001")
    sim.run_all()
    assert "dead state" in _hot(sim.diagram.view, "q_trap", ad._HotEllipse).tip
    assert any(i.tip.startswith("δ(q3, 2) = q_trap") for i in sim.diagram.view._scene.items() if isinstance(i, ad._HotPath))


def test_nfa_epsilon_edges_are_explained(sim) -> None:
    sim.model.setCurrentIndex(sim.model.findData("NFA"))
    sim.load("EMP")
    assert "ε-closure follows these edges" in _hot(sim.diagram.view, "ε-move n1", ad._HotPath).tip


# --- RE segments on the tape -----------------------------------------------------------------------------

def test_tape_bars_follow_the_regular_expression_parts(qapp) -> None:
    tape = TapeView()
    tape.load("EMP-2026-0042", segments=ID_SEGMENTS)
    bars = [b.property("seg") for b in tape.findChildren(QWidget) if b.objectName() == "TapeSeg"]
    assert bars == ["a"] * 3 + ["b"] + ["a"] * 4 + ["b"] + ["a"] * 4


def test_extra_symbols_beyond_the_regex_have_no_segment(qapp) -> None:
    tape = TapeView()
    tape.load("EMP-2026-00421", segments=ID_SEGMENTS)
    bars = [b.property("seg") for b in tape.findChildren(QWidget) if b.objectName() == "TapeSeg"]
    assert bars[-1] == "none" and len(bars) == 14
    assert "prefix" in segment_legend(ID_SEGMENTS) and "year YYYY" in segment_legend(ID_SEGMENTS)


# --- accessibility ------------------------------------------------------------------------------------------

def test_key_widgets_have_accessible_names(sim, window) -> None:
    assert sim.input.accessibleName() == "Employee ID"
    assert {b.accessibleName() for b in (sim.btn_prev, sim.btn_play, sim.btn_step, sim.btn_all, sim.btn_reset)} \
        == {"Prev", "Play", "Step", "Run all", "Reset"}
    assert sim.history.accessibleName() == "Transition history" and sim.tape.accessibleName() == "Input tape"
    assert [b.accessibleName() for b in window.nav] == ["Simulate view", "Theory view", "Tests view"]


def test_screen_reader_text_tracks_the_run(sim) -> None:
    sim.load("EMP-2026-0042")
    sim.step_forward()
    assert sim.tape.accessibleDescription().startswith("1 of 13 symbols read")
    assert "Current state: q1" in sim.diagram.view.accessibleDescription()
    sim.run_all()
    assert sim.banner.accessibleName().startswith("Result: ACCEPTED")


def test_controls_are_keyboard_focusable_but_not_mouse_focus_stealers(sim) -> None:
    for b in (sim.btn_prev, sim.btn_play, sim.btn_step, sim.btn_all, sim.btn_reset, sim.btn_load):
        assert b.focusPolicy() == Qt.FocusPolicy.TabFocus


def test_space_activates_the_focused_button_otherwise_toggles_play(sim, monkeypatch) -> None:
    sim.load("EMP-2026-0042")
    sim.step_forward()
    monkeypatch.setattr(QApplication, "focusWidget", staticmethod(lambda: sim.btn_reset))
    sim._space()                                             # focused Reset is clicked, not Play
    assert sim.history.rowCount() == 0 and not sim._timer.isActive()
    monkeypatch.setattr(QApplication, "focusWidget", staticmethod(lambda: sim.input))
    sim._space()
    assert sim._timer.isActive()
    sim._space()
    assert not sim._timer.isActive()


# --- fonts / theme -------------------------------------------------------------------------------------------

def test_font_loader_is_safe_without_bundled_fonts(qapp) -> None:
    assert isinstance(theme.load_fonts(), list)


def test_segment_colours_meet_graphics_contrast() -> None:
    assert theme.contrast(P["seg_a"], P["surface"]) >= 3 and theme.contrast(P["seg_b"], P["surface"]) >= 3
