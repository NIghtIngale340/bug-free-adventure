from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFrame, QLineEdit, QLabel, QPushButton, QGridLayout,
)


class LandingPage(QWidget):
    """Single input box for Employee ID with quick presets & test suite navigation."""

    def __init__(self, on_submit, on_open_test_cases=None, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._on_submit = on_submit
        self._on_open_test_cases = on_open_test_cases

        card = QFrame()
        card.setObjectName("LandingCard")
        card.setFixedSize(560, 390)

        eyebrow = QLabel("EMPLOYEE ID VALIDATOR")
        eyebrow.setObjectName("LandingTitle")
        eyebrow.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self._input = QLineEdit()
        self._input.setObjectName("LandingInput")
        self._input.setPlaceholderText("EMP-2026-0042")
        self._input.setFixedWidth(380)
        self._input.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._input.setMaxLength(32)
        self._input.returnPressed.connect(self._submit)

        label = QLabel("Enter Your Employee ID")
        label.setObjectName("LandingLabel")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        hint = QLabel("Press Enter or click a preset below to run through the DFA simulator")
        hint.setObjectName("LandingHint")
        hint.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self._error_label = QLabel("")
        self._error_label.setObjectName("LandingError")
        self._error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._error_label.setFixedHeight(18)

        # Quick Presets for Live Demo
        presets_label = QLabel("Quick Presets for Live Demo:")
        presets_label.setObjectName("LandingHint")
        presets_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        presets = [
            ("✔ Valid 2026", "EMP-2026-0042"),
            ("✔ Valid 2099", "EMP-2099-9999"),
            ("✘ Invalid Char", "EMP-2026-12A4"),
            ("✘ No Hyphen", "EMP2026-0001"),
            ("✘ Short Year", "EMP-26-0001"),
            ("✘ Bad Prefix", "AXP-2026-0001"),
        ]

        presets_grid = QGridLayout()
        presets_grid.setSpacing(6)
        for i, (name, val) in enumerate(presets):
            btn = QPushButton(name)
            btn.setObjectName("PresetButton")
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda _, v=val: self._load_and_submit(v))
            presets_grid.addWidget(btn, i // 3, i % 3)

        # Open Test Suite Button
        self._test_suite_btn = QPushButton("📋 Open Predefined Test Suite (28 Test Cases)  →")
        self._test_suite_btn.setObjectName("SecondaryButton")
        self._test_suite_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._test_suite_btn.clicked.connect(self._open_tests)

        card_layout = QVBoxLayout(card)
        card_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.setSpacing(8)
        card_layout.addStretch()
        card_layout.addWidget(eyebrow)
        card_layout.addSpacing(4)
        card_layout.addWidget(self._input, alignment=Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(label, alignment=Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(hint, alignment=Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(self._error_label, alignment=Qt.AlignmentFlag.AlignCenter)
        card_layout.addSpacing(4)
        card_layout.addWidget(presets_label, alignment=Qt.AlignmentFlag.AlignCenter)
        card_layout.addLayout(presets_grid)
        card_layout.addSpacing(8)
        card_layout.addWidget(self._test_suite_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        card_layout.addStretch()

        outer = QVBoxLayout(self)
        outer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        outer.addWidget(card, alignment=Qt.AlignmentFlag.AlignCenter)

    def _load_and_submit(self, value: str) -> None:
        self._input.setText(value)
        self._submit()

    def _open_tests(self) -> None:
        if self._on_open_test_cases:
            self._on_open_test_cases()

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