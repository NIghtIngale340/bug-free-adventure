from PySide6.QtCore import Qt
from PySide6.QtWidgets import QHBoxLayout, QLabel, QVBoxLayout, QWidget, QFrame

class StateView(QWidget):
    """Character ribbon + current/next state badges for the simulator."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        self._ribbon_layout = QHBoxLayout()
        self._ribbon_layout.setSpacing(4)
        ribbon_container = QFrame()
        ribbon_container.setObjectName("RibbonContainer")
        ribbon_container.setLayout(self._ribbon_layout)

        self._current_state_badge = QLabel("Current State: —")
        self._current_state_badge.setObjectName("CurrentStateBadge")
        self._next_state_badge = QLabel("Next State: —")
        self._next_state_badge.setObjectName("NextStateBadge")

        badges = QHBoxLayout()
        badges.addWidget(self._current_state_badge)
        badges.addStretch()
        badges.addWidget(self._next_state_badge)

        layout = QVBoxLayout(self)
        layout.addWidget(ribbon_container)
        layout.addLayout(badges)

        self._cells: list[QLabel] = []

    def load_string(self, input_string: str) -> None:
        while self._ribbon_layout.count():
            item = self._ribbon_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self._cells.clear()

        for ch in input_string:
            cell = QLabel(ch)
            cell.setObjectName("RibbonCell")
            cell.setAlignment(Qt.AlignCenter)
            cell.setFixedSize(34, 34)
            self._ribbon_layout.addWidget(cell)
            self._cells.append(cell)
        self._ribbon_layout.addStretch()
        self.set_cursor(-1)
        self.set_states(None, None)

    def set_cursor(self, index: int) -> None:
        for i, cell in enumerate(self._cells):
            cell.setProperty("active", i == index)
            cell.setProperty("done", i < index)
            cell.style().unpolish(cell)
            cell.style().polish(cell)

    def set_states(self, current: str | None, nxt: str | None, mode: str = "DFA") -> None:
        curr_label = "Current Subset (NFA)" if mode == "NFA" else "Current State"
        next_label = "Next Subset (NFA)" if mode == "NFA" else "Next State"
        self._current_state_badge.setText(f"{curr_label}: {current or '—'}")
        self._next_state_badge.setText(f"{next_label}: {nxt or '—'}")