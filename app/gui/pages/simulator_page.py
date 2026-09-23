from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QPushButton, QSizePolicy,
)

from app.gui.widgets.state_view import StateView
from app.gui.widgets.state_diagram_view import StateDiagramView
from app.gui.widgets.result_overlay import ResultOverlay


class SimulatorPage(QWidget):
    """Full-page, animated step-by-step DFA run. Result appears as an in-page
    overlay stacked in the SAME grid cell as the page content. Once the run
    finishes, a 'View Automata Theory' button becomes available bottom-right."""

    def __init__(self, simulation_service, accepting_states, on_check_another,
                 on_view_automata, parent=None) -> None:
        super().__init__(parent)
        self._service = simulation_service
        self._on_check_another = on_check_another
        self._on_view_automata = on_view_automata
        self._last_result = None
        self._session_id: str | None = None
        self._loaded_string: str = ""
        self._cursor: int = 0

        self._timer = QTimer(self)
        self._timer.setInterval(600)
        self._timer.timeout.connect(self._tick)

        # ---- page content (everything except the overlay) ----
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

        self._diagram = StateDiagramView(accepting_states)
        self._diagram.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

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
        bottom_row.addStretch()
        bottom_row.addWidget(self._automata_btn)

        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(28, 20, 28, 20)
        content_layout.setSpacing(14)
        content_layout.addLayout(header_row)
        content_layout.addWidget(self._state_view)
        content_layout.addWidget(self._diagram, 1)
        content_layout.addLayout(bottom_row)

        # ---- overlay, stacked on top of content via the grid ----
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
        self._session_id = self._service.create_session(input_string)

        self._state_view.load_string(input_string)
        self._state_view.set_states("q0", None)
        self._diagram.reset()
        self._diagram.highlight("q0")
        self._status_label.setText(f'Processing "{input_string}" symbol by symbol…')

        self._timer.start()

    def _tick(self) -> None:
        step = self._service.step(self._session_id)
        if step is None:
            self._finish()
            return

        trapped = step.to_state == "q_trap"
        self._state_view.set_cursor(self._cursor)
        self._state_view.set_states(step.from_state, step.to_state)
        self._diagram.highlight(step.to_state, trapped=trapped)
        self._cursor += 1

        if trapped or self._cursor >= len(self._loaded_string):
            self._finish()

    def _finish(self) -> None:
        self._timer.stop()
        result = self._service.validate(self._loaded_string)
        self._last_result = result   # <-- add this line
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

    def _on_view_automata_clicked(self) -> None:
        self._overlay.dismiss(silent=True)
        self._on_view_automata()

    def refresh_view(self) -> None:
        """Force a full repaint of the diagram viewport and the result overlay
        (if visible) — called by MainWindow when the window regains activation
        (alt-tab / minimize-restore) to clear any stale black regions."""
        self._diagram.viewport().update()
        self.update()
        self._overlay.refresh()