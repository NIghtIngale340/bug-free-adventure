from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QVBoxLayout, QWidget

from app.core.models import SimulationResult, SimulationStatus
from app.gui.a11y import announce
from app.gui.widgets.tape_view import repolish

_STATUS_TEXT = {
    SimulationStatus.ACCEPTED: "reached an accepting state",
    SimulationStatus.REJECTED_INVALID_SYMBOL: "symbol outside Σ (Layer 1)",
    SimulationStatus.REJECTED_NO_TRANSITION: "fell into the dead state",
    SimulationStatus.REJECTED_NON_FINAL_STATE: "input ended in a non-accepting state",
    SimulationStatus.REJECTED_EMPTY_INPUT: "empty input",
}


class VerdictBanner(QFrame):
    """Inline ACCEPTED / REJECTED strip: verdict, the reason, and the final-state facts."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("Banner")
        self._title = QLabel()
        self._title.setObjectName("BannerTitle")
        self._text = QLabel()
        self._text.setObjectName("BannerText")
        self._text.setWordWrap(True)
        self._meta = QLabel()
        self._meta.setObjectName("Muted")
        self._meta.setWordWrap(True)
        self._title.setMinimumWidth(150)
        detail = QVBoxLayout()
        detail.setSpacing(0)
        detail.addWidget(self._text)
        detail.addWidget(self._meta)
        lay = QHBoxLayout(self)                      # compact: verdict on the left, reason + facts on the right
        lay.setContentsMargins(16, 8, 16, 8)
        lay.setSpacing(18)
        lay.addWidget(self._title, 0, Qt.AlignmentFlag.AlignVCenter)
        lay.addLayout(detail, 1)
        self.show_idle("Load an Employee ID, then press Step or Play.")

    def _set(self, state: str, title: str, text: str, meta: str = "") -> None:
        self.setProperty("state", state)
        self._title.setText(title)
        self._text.setText(text)
        self._meta.setText(meta)
        self._meta.setVisible(bool(meta))
        self.setAccessibleName(f"Result: {title}. {text}")
        self.setAccessibleDescription(meta)
        repolish(self)
        for w in (self._title, self._text):
            repolish(w)

    def show_idle(self, text: str) -> None:
        self._set("idle", "READY", text)

    def show_running(self, text: str) -> None:
        self._set("running", "RUNNING", text)

    def show_result(self, r: SimulationResult) -> None:
        meta = (f"Final state: {r.final_state or '—'}   ·   automaton consumed "
                f"{r.processed_symbols} of {r.total_symbols} symbols   ·   {_STATUS_TEXT[r.status]}")
        self._set("accepted" if r.accepted else "rejected",
                  "ACCEPTED" if r.accepted else "REJECTED", r.explanation, meta)
        announce(self)
