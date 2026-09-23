from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QPushButton,
    QSizePolicy, QSlider, QFrame,
)

from app.gui.widgets.state_view import StateView
from app.gui.widgets.state_diagram_view import StateDiagramView
from app.gui.widgets.result_overlay import ResultOverlay


class SimulatorPage(QWidget):
    """Full-page, animated step-by-step DFA run with interactive playback controls.
    
    Includes manual stepping ('Next Step'), play/pause, fast-forward, reset,
    speed control slider, and live mathematical transition formula callouts.
    """

    def __init__(self, simulation_service, accepting_states, on_check_another,
                 on_view_automata, on_view_tests=None, parent=None) -> None:
        super().__init__(parent)
        self._service = simulation_service
        self._on_check_another = on_check_another
        self._on_view_automata = on_view_automata
        self._on_view_tests = on_view_tests
        self._last_result = None
        self._session_id: str | None = None
        self._loaded_string: str = ""
        self._cursor: int = 0
        self._is_paused: bool = False

        self._timer = QTimer(self)
        self._interval_ms = 600
        self._timer.setInterval(self._interval_ms)
        self._timer.timeout.connect(self._tick)

        # ---- page content ----
        content = QWidget(self)

        back_btn = QPushButton("←  Back")
        back_btn.setObjectName("GhostButton")
        back_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        back_btn.clicked.connect(self._cancel_and_back)

        title = QLabel("DFA Simulation")
        title.setObjectName("PageTitle")

        self._status_label = QLabel("")
        self._status_label.setObjectName("PageSubtitle")

        header_text = QVBoxLayout()
        header_text.setSpacing(2)
        header_text.addWidget(title)
        header_text.addWidget(self._status_label)

        header_row = QHBoxLayout()
        header_row.addWidget(back_btn)
        header_row.addSpacing(16)
        header_row.addLayout(header_text)
        header_row.addStretch()

        self._state_view = StateView()

        # Mathematical Delta Callout
        self._callout_label = QLabel("Awaiting start...")
        self._callout_label.setObjectName("StepCallout")
        self._callout_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self._diagram = StateDiagramView(accepting_states)
        self._diagram.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        # ---- Interactive Playback Control Bar ----
        control_bar = QFrame()
        control_bar.setObjectName("ControlBar")
        control_layout = QHBoxLayout(control_bar)
        control_layout.setContentsMargins(12, 6, 12, 6)
        control_layout.setSpacing(10)

        self._pause_btn = QPushButton("⏸  Pause")
        self._pause_btn.setObjectName("ControlBarButton")
        self._pause_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._pause_btn.clicked.connect(self._toggle_pause)

        self._next_step_btn = QPushButton("⏭  Next Step")
        self._next_step_btn.setObjectName("ControlBarButton")
        self._next_step_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._next_step_btn.clicked.connect(self._manual_step)

        self._fast_forward_btn = QPushButton("⏩  Fast-Forward")
        self._fast_forward_btn.setObjectName("ControlBarButton")
        self._fast_forward_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._fast_forward_btn.clicked.connect(self._fast_forward)

        self._restart_btn = QPushButton("↺  Restart")
        self._restart_btn.setObjectName("ControlBarButton")
        self._restart_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._restart_btn.clicked.connect(self._restart)

        # Speed Slider
        self._speed_label = QLabel("Speed: 1.0x")
        self._speed_label.setObjectName("PageSubtitle")
        self._speed_label.setFixedWidth(75)

        self._speed_slider = QSlider(Qt.Orientation.Horizontal)
        self._speed_slider.setRange(200, 1200)
        self._speed_slider.setValue(600)
        self._speed_slider.setFixedWidth(110)
        self._speed_slider.setCursor(Qt.CursorShape.PointingHandCursor)
        self._speed_slider.valueChanged.connect(self._on_speed_changed)

        control_layout.addWidget(self._pause_btn)
        control_layout.addWidget(self._next_step_btn)
        control_layout.addWidget(self._fast_forward_btn)
        control_layout.addWidget(self._restart_btn)
        control_layout.addStretch()
        control_layout.addWidget(self._speed_label)
        control_layout.addWidget(self._speed_slider)

        # Bottom Actions
        check_another_btn = QPushButton("Check Another ID")
        check_another_btn.setObjectName("PrimaryButton")
        check_another_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        check_another_btn.clicked.connect(self._cancel_and_back)

        self._automata_btn = QPushButton("View Automata Theory  →")
        self._automata_btn.setObjectName("SecondaryButton")
        self._automata_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._automata_btn.setEnabled(False)
        self._automata_btn.clicked.connect(self._on_view_automata_clicked)

        bottom_row = QHBoxLayout()
        bottom_row.addWidget(check_another_btn)
        if self._on_view_tests:
            test_suite_btn = QPushButton("📋  Test Suite")
            test_suite_btn.setObjectName("SecondaryButton")
            test_suite_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            test_suite_btn.clicked.connect(self._on_view_tests_clicked)
            bottom_row.addWidget(test_suite_btn)
        bottom_row.addStretch()
        bottom_row.addWidget(self._automata_btn)

        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(28, 16, 28, 16)
        content_layout.setSpacing(10)
        content_layout.addLayout(header_row)
        content_layout.addWidget(self._state_view)
        content_layout.addWidget(self._callout_label)
        content_layout.addWidget(control_bar)
        content_layout.addWidget(self._diagram, 1)
        content_layout.addLayout(bottom_row)

        # ---- overlay stacked via grid ----
        self._overlay = ResultOverlay(self)

        root = QGridLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.addWidget(content, 0, 0)
        root.addWidget(self._overlay, 0, 0)

    def load_and_run(self, input_string: str) -> None:
        self._timer.stop()
        self._overlay.dismiss(silent=True)
        self._automata_btn.setEnabled(False)
        self._loaded_string = input_string
        self._cursor = 0
        self._is_paused = False
        self._pause_btn.setText("⏸  Pause")
        self._pause_btn.setEnabled(True)
        self._next_step_btn.setEnabled(True)
        self._fast_forward_btn.setEnabled(True)
        self._restart_btn.setEnabled(True)

        self._session_id = self._service.create_session(input_string)

        self._state_view.load_string(input_string)
        self._state_view.set_states("q0", None)
        self._diagram.reset()
        self._diagram.highlight("q0")
        self._status_label.setText(f'Processing "{input_string}" symbol by symbol…')
        self._callout_label.setText("Start state: q0 (Ready to evaluate first symbol)")
        self._callout_label.setStyleSheet("color: #E5E7EB;")

        self._timer.start()

    def _toggle_pause(self) -> None:
        if self._is_paused:
            self._is_paused = False
            self._pause_btn.setText("⏸  Pause")
            self._status_label.setText(f'Processing "{self._loaded_string}" symbol by symbol…')
            self._timer.start()
        else:
            self._is_paused = True
            self._timer.stop()
            self._pause_btn.setText("▶  Resume")
            self._status_label.setText("Simulation paused. Click 'Next Step' or 'Resume'.")

    def _manual_step(self) -> None:
        if not self._is_paused:
            self._toggle_pause()
        self._tick()

    def _fast_forward(self) -> None:
        self._timer.stop()
        while self._cursor < len(self._loaded_string):
            step = self._service.step(self._session_id)
            if step is None:
                break
            trapped = (step.to_state == "q_trap")
            self._state_view.set_cursor(self._cursor)
            self._state_view.set_states(step.from_state, step.to_state)
            self._diagram.highlight(step.to_state, trapped=trapped)
            self._cursor += 1
            if trapped:
                break
        self._finish()

    def _restart(self) -> None:
        self.load_and_run(self._loaded_string)

    def _on_speed_changed(self, value: int) -> None:
        # Value ranges from 200 (fast) to 1200 (slow)
        # Slider is inverted: left (slow) to right (fast)
        inverted_val = 1400 - value
        self._interval_ms = inverted_val
        self._timer.setInterval(self._interval_ms)
        speed_factor = 600.0 / inverted_val
        self._speed_label.setText(f"Speed: {speed_factor:.1f}x")

    def _tick(self) -> None:
        step = self._service.step(self._session_id)
        if step is None:
            self._finish()
            return

        trapped = (step.to_state == "q_trap")
        self._state_view.set_cursor(self._cursor)
        self._state_view.set_states(step.from_state, step.to_state)
        self._diagram.highlight(step.to_state, trapped=trapped)
        self._cursor += 1

        # Live Mathematical Delta Callout
        if trapped:
            self._callout_label.setText(
                f"Step {step.step}:  δ({step.from_state}, '{step.symbol}') = q_trap  —  ✘ {step.explanation}"
            )
            self._callout_label.setStyleSheet("color: #F87171; font-weight: bold;")
        else:
            self._callout_label.setText(
                f"Step {step.step}:  δ({step.from_state}, '{step.symbol}') = {step.to_state}  —  ✓ {step.explanation}"
            )
            self._callout_label.setStyleSheet("color: #34D399; font-weight: bold;")

        if trapped or self._cursor >= len(self._loaded_string):
            self._finish()

    def _finish(self) -> None:
        self._timer.stop()
        self._pause_btn.setEnabled(False)
        self._next_step_btn.setEnabled(False)
        self._fast_forward_btn.setEnabled(False)

        result = self._service.validate(self._loaded_string)
        self._last_result = result
        self._diagram.highlight(
            result.final_state, trapped=(result.final_state == "q_trap"), finished=True
        )
        self._status_label.setText("Simulation complete.")
        self._automata_btn.setEnabled(True)
        QTimer.singleShot(450, lambda: self._overlay.show_result(result))

    def get_last_result(self):
        return self._last_result

    def _cancel_and_back(self) -> None:
        self._timer.stop()
        self._overlay.dismiss(silent=True)
        if self._session_id:
            self._service.reset(self._session_id)
        self._on_check_another()

    def _on_view_tests_clicked(self) -> None:
        self._timer.stop()
        self._overlay.dismiss(silent=True)
        if self._on_view_tests:
            self._on_view_tests()

    def _on_view_automata_clicked(self) -> None:
        self._overlay.dismiss(silent=True)
        self._on_view_automata()

    def refresh_view(self) -> None:
        self._diagram.viewport().update()
        self.update()
        self._overlay.refresh()