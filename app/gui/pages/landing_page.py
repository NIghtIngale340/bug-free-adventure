from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QFrame, QLineEdit, QLabel

class LandingPage(QWidget):
    """ a single input box for the Employee ID.
    No character filtering happens here — any text the user types is passed
    through untouched. Whether the string is valid (correct alphabet, correct
    structure) is entirely the DFA/service layer's decision, surfaced on the
    Simulator Page as it steps through (or traps on) the input.
    """
    def __init__(self, on_submit, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._on_submit = on_submit

        card = QFrame()
        card.setObjectName("LandingCard")
        card.setFixedSize(520, 300)

        eyebrow = QLabel("EMPLOYEE ID VALIDATOR")
        eyebrow.setObjectName("LandingTitle")
        eyebrow.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self._input = QLineEdit()
        self._input.setObjectName("LandingInput")
        self._input.setPlaceholderText("EMP-2026-0042")
        self._input.setFixedWidth(360)
        self._input.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._input.setMaxLength(32)
        self._input.returnPressed.connect(self._submit)

        label = QLabel("Enter Your Employee ID")
        label.setObjectName("LandingLabel")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        hint = QLabel("Press Enter to run it through the DFA simulator")
        hint.setObjectName("LandingHint")
        hint.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self._error_label = QLabel("")
        self._error_label.setObjectName("LandingError")
        self._error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._error_label.setFixedHeight(18)

        card_layout = QVBoxLayout(card)
        card_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.setSpacing(12)
        card_layout.addStretch()
        card_layout.addWidget(eyebrow)
        card_layout.addSpacing(6)
        card_layout.addWidget(self._input, alignment=Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(label, alignment=Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(hint, alignment=Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(self._error_label, alignment=Qt.AlignmentFlag.AlignCenter)
        card_layout.addStretch()

        outer = QVBoxLayout(self)
        outer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        outer.addWidget(card, alignment=Qt.AlignmentFlag.AlignCenter)

    def _submit(self) -> None:
        text = self._input.text().strip()
        if not text:
            self._error_label.setText("Please enter an Employee ID.")
            return
        self._error_label.setText("")
        self._on_submit(text)

    def clear(self) -> None:
        self._input.clear()
        self._error_label.setText("")