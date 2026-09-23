from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPainter, QPen, QColor
from PySide6.QtWidgets import QFrame, QLabel, QVBoxLayout, QHBoxLayout, QWidget, QPushButton

from app.core.models import SimulationResult

class _CloseIconButton(QPushButton):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("ModalCloseButton")
        self.setFixedSize(28, 28)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    def paintEvent(self, event) -> None:
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        color = QColor("#F3F4F6") if self.underMouse() else QColor("#8B95A5")
        pen = QPen(color, 1.6)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)

        margin = 9
        rect = self.rect()
        painter.drawLine(rect.left() + margin, rect.top() + margin,
                          rect.right() - margin, rect.bottom() - margin)
        painter.drawLine(rect.right() - margin, rect.top() + margin,
                          rect.left() + margin, rect.bottom() - margin)

    def enterEvent(self, event) -> None:
        super().enterEvent(event)
        self.update()

    def leaveEvent(self, event) -> None:
        super().leaveEvent(event)
        self.update()


class ResultCard(QFrame):
    """Big ACCEPTED / REJECTED banner with readout fields and a built-in
    close button (shown only when used inside an overlay/modal context)."""

    closeRequested = Signal()

    def __init__(self, parent: QWidget | None = None, show_close_button: bool = False) -> None:
        super().__init__(parent)
        self.setObjectName("ResultCard")
        self.setFrameShape(QFrame.Shape.StyledPanel)

        self._close_btn = _CloseIconButton(self)
        self._close_btn.clicked.connect(self.closeRequested.emit)
        self._close_btn.setVisible(show_close_button)

        close_row = QHBoxLayout()
        close_row.setContentsMargins(0, 0, 0, 0)
        close_row.addStretch()
        close_row.addWidget(self._close_btn)

        self._status_label = QLabel("—")
        self._status_label.setObjectName("StatusLabel")
        self._status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self._final_state_label = QLabel("Final State: —")
        self._symbols_label = QLabel("Symbols Processed: —")
        self._explanation_label = QLabel("Enter an Employee ID and click Validate.")
        self._explanation_label.setWordWrap(True)

        readout = QHBoxLayout()
        readout.addWidget(self._final_state_label)
        readout.addStretch()
        readout.addWidget(self._symbols_label)

        layout = QVBoxLayout(self)
        layout.addLayout(close_row)
        layout.addWidget(self._status_label)
        layout.addLayout(readout)
        layout.addWidget(self._explanation_label)

        self.show_idle()

    def set_close_button_visible(self, visible: bool) -> None:
        self._close_btn.setVisible(visible)

    def show_idle(self) -> None:
        self._status_label.setText("—")
        self._status_label.setProperty("state", "idle")
        self._final_state_label.setText("Final State: —")
        self._symbols_label.setText("Symbols Processed: —")
        self._explanation_label.setText("Enter an Employee ID and click Validate.")
        self._refresh_style()

    def show_warning(self, message: str) -> None:
        self._status_label.setText("⚠ INPUT REQUIRED")
        self._status_label.setProperty("state", "warning")
        self._final_state_label.setText("Final State: —")
        self._symbols_label.setText("Symbols Processed: —")
        self._explanation_label.setText(message)
        self._refresh_style()

    def show_result(self, result: SimulationResult) -> None:
        if result.accepted:
            self._status_label.setText("✔ ACCEPTED")
            self._status_label.setProperty("state", "accepted")
        else:
            self._status_label.setText("✘ REJECTED")
            self._status_label.setProperty("state", "rejected")

        self._final_state_label.setText(f"Final State: {result.final_state or '—'}")
        self._symbols_label.setText(
            f"Symbols Processed: {result.processed_symbols} / {result.total_symbols}"
        )
        self._explanation_label.setText(result.explanation)
        self._refresh_style()

    def _refresh_style(self) -> None:
        self._status_label.style().unpolish(self._status_label)
        self._status_label.style().polish(self._status_label)