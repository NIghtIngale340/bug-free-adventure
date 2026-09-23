from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTableWidget,
    QTableWidgetItem, QHeaderView, QFrame, QButtonGroup,
)

from app.data.test_cases import MASTER_TEST_SUITE, TestCase


class TestCasesPage(QWidget):
    """Predefined Test Suite Runner.
    
    Executes all 28 categorized test cases against the real Minimized DFA engine.
    Allows filtering by category and single-click loading into the step-by-step
    simulator for live visual verification.
    """

    def __init__(self, simulation_service, on_select_test, on_back, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._service = simulation_service
        self._on_select_test = on_select_test
        self._on_back = on_back

        self._filter = "all"  # "all", "valid", "invalid"
        self._results: dict[str, tuple[bool, bool]] = {}  # id -> (expected, actual)

        # Header Row
        back_btn = QPushButton("←  Back")
        back_btn.setObjectName("GhostButton")
        back_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        back_btn.clicked.connect(self._on_back)

        title = QLabel("Predefined Test Suite")
        title.setObjectName("PageTitle")

        subtitle = QLabel("28 Categorized Test Cases from Formal Automata Specification")
        subtitle.setObjectName("PageSubtitle")

        header_text = QVBoxLayout()
        header_text.setSpacing(2)
        header_text.addWidget(title)
        header_text.addWidget(subtitle)

        header_row = QHBoxLayout()
        header_row.addWidget(back_btn)
        header_row.addSpacing(16)
        header_row.addLayout(header_text)
        header_row.addStretch()

        # Control Bar
        self._run_all_btn = QPushButton("▶  Run All 28 Test Cases")
        self._run_all_btn.setObjectName("PrimaryButton")
        self._run_all_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._run_all_btn.clicked.connect(self.run_all_tests)

        self._stats_label = QLabel("Click 'Run All' to evaluate tests through the Minimized DFA.")
        self._stats_label.setObjectName("PageSubtitle")

        self._btn_all = QPushButton("All (28)")
        self._btn_all.setObjectName("FilterButton")
        self._btn_all.setProperty("active", True)
        self._btn_all.setCursor(Qt.CursorShape.PointingHandCursor)
        self._btn_all.clicked.connect(lambda: self._set_filter("all"))

        self._btn_valid = QPushButton("Valid Only (10)")
        self._btn_valid.setObjectName("FilterButton")
        self._btn_valid.setProperty("active", False)
        self._btn_valid.setCursor(Qt.CursorShape.PointingHandCursor)
        self._btn_valid.clicked.connect(lambda: self._set_filter("valid"))

        self._btn_invalid = QPushButton("Invalid Only (18)")
        self._btn_invalid.setObjectName("FilterButton")
        self._btn_invalid.setProperty("active", False)
        self._btn_invalid.setCursor(Qt.CursorShape.PointingHandCursor)
        self._btn_invalid.clicked.connect(lambda: self._set_filter("invalid"))

        controls_row = QHBoxLayout()
        controls_row.addWidget(self._run_all_btn)
        controls_row.addSpacing(16)
        controls_row.addWidget(self._btn_all)
        controls_row.addWidget(self._btn_valid)
        controls_row.addWidget(self._btn_invalid)
        controls_row.addStretch()
        controls_row.addWidget(self._stats_label)

        # Results Table
        self._table = QTableWidget()
        self._table.setObjectName("MatrixTable")
        self._table.setColumnCount(7)
        self._table.setHorizontalHeaderLabels([
            "Test ID", "Category", "Input String", "Expected", "Actual", "Status", "Simulate"
        ])
        self._table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self._table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self._table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self._table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        self._table.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
        self._table.horizontalHeader().setSectionResizeMode(6, QHeaderView.ResizeMode.ResizeToContents)
        self._table.verticalHeader().setVisible(False)
        self._table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

        # Layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 20, 28, 20)
        layout.setSpacing(14)
        layout.addLayout(header_row)
        layout.addLayout(controls_row)
        layout.addWidget(self._table, 1)

        # Populate table and run initially
        self._populate_table()
        self.run_all_tests()

    def _set_filter(self, filter_mode: str) -> None:
        self._filter = filter_mode
        self._btn_all.setProperty("active", filter_mode == "all")
        self._btn_valid.setProperty("active", filter_mode == "valid")
        self._btn_invalid.setProperty("active", filter_mode == "invalid")
        for btn in (self._btn_all, self._btn_valid, self._btn_invalid):
            btn.style().unpolish(btn)
            btn.style().polish(btn)
        self._populate_table()

    def _filtered_tests(self) -> list[TestCase]:
        if self._filter == "valid":
            return [tc for tc in MASTER_TEST_SUITE if tc.expected_accepted]
        if self._filter == "invalid":
            return [tc for tc in MASTER_TEST_SUITE if not tc.expected_accepted]
        return list(MASTER_TEST_SUITE)

    def _populate_table(self) -> None:
        tests = self._filtered_tests()
        self._table.setRowCount(len(tests))

        for row, tc in enumerate(tests):
            # Test ID
            item_id = QTableWidgetItem(tc.id)
            item_id.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self._table.setItem(row, 0, item_id)

            # Category
            item_cat = QTableWidgetItem(tc.category)
            self._table.setItem(row, 1, item_cat)

            # Input String
            disp_input = repr(tc.input_str) if tc.input_str == "" else tc.input_str
            item_input = QTableWidgetItem(disp_input)
            item_input.setFont(QFont := item_input.font())
            self._table.setItem(row, 2, item_input)

            # Expected
            expected_text = "ACCEPTED" if tc.expected_accepted else "REJECTED"
            item_exp = QTableWidgetItem(expected_text)
            item_exp.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self._table.setItem(row, 3, item_exp)

            # Actual & Status
            if tc.id in self._results:
                expected, actual = self._results[tc.id]
                actual_text = "ACCEPTED" if actual else "REJECTED"
                item_act = QTableWidgetItem(actual_text)
                item_act.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self._table.setItem(row, 4, item_act)

                status_text = "✔ PASS" if (expected == actual) else "✘ FAIL"
                item_status = QTableWidgetItem(status_text)
                item_status.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                if expected == actual:
                    item_status.setForeground(QColor("#34D399"))
                else:
                    item_status.setForeground(QColor("#F87171"))
                self._table.setItem(row, 5, item_status)
            else:
                self._table.setItem(row, 4, QTableWidgetItem("—"))
                self._table.setItem(row, 5, QTableWidgetItem("—"))

            # Simulate Button
            sim_btn = QPushButton("🔍 Simulate")
            sim_btn.setObjectName("GhostButton")
            sim_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            sim_btn.clicked.connect(lambda _, s=tc.input_str: self._on_select_test(s))
            self._table.setCellWidget(row, 6, sim_btn)

    def run_all_tests(self) -> None:
        passed = 0
        total = len(MASTER_TEST_SUITE)

        for tc in MASTER_TEST_SUITE:
            res = self._service.validate(tc.input_str)
            actual_accepted = bool(res.accepted)
            self._results[tc.id] = (tc.expected_accepted, actual_accepted)
            if actual_accepted == tc.expected_accepted:
                passed += 1

        self._stats_label.setText(
            f"Results: {passed} / {total} PASSED ({100.0 * passed / total:.1f}%) — Verified with Minimized DFA"
        )
        if passed == total:
            self._stats_label.setStyleSheet("color: #34D399; font-weight: bold;")
        else:
            self._stats_label.setStyleSheet("color: #F87171; font-weight: bold;")

        self._populate_table()
