from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QPlainTextEdit,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from app.data.test_cases import MASTER_TEST_SUITE
from app.gui.a11y import label as a11y
from app.gui.theme import PALETTE as P

_MODES = ("DFA", "SUBSET", "NFA")


def _shown(s: str) -> str:
    return "(empty)" if s == "" else (repr(s) if s != s.strip() else s)


def _table(headers: list[str]) -> QTableWidget:
    t = QTableWidget(0, len(headers))
    t.setHorizontalHeaderLabels(headers)
    t.verticalHeader().setVisible(False)
    t.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
    t.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
    hh = t.horizontalHeader()
    hh.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
    hh.setStretchLastSection(True)
    return t


def _cell(text: str, color: str | None = None, center: bool = False) -> QTableWidgetItem:
    item = QTableWidgetItem(text)
    if color:
        item.setForeground(QColor(color))
    if center:
        item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
    return item


class TestsPage(QWidget):
    """Predefined suite (expected vs. actual, all three models) and free-form batch validation."""

    __test__ = False
    simulateRequested = Signal(str)

    def __init__(self, service, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._service = service

        self.stats = QLabel()
        self.stats.setObjectName("Muted")
        run = QPushButton("Run all")
        run.setObjectName("PrimaryButton")
        run.clicked.connect(self.run_suite)
        bar = QHBoxLayout()
        bar.addWidget(run)
        bar.addWidget(self.stats, 1)
        self.suite = _table(["Test ID", "Category", "Input", "Expected", "Actual", "Result", "Models agree", "Reason", ""])
        self.suite.setRowCount(len(MASTER_TEST_SUITE))
        a11y(self.suite, "Predefined test suite results", "Expected versus actual verdict for each test input")
        suite_page = QWidget()
        sl = QVBoxLayout(suite_page)
        sl.setContentsMargins(0, 12, 0, 0)
        sl.addLayout(bar)
        sl.addWidget(self.suite, 1)

        self.batch_in = QPlainTextEdit()
        self.batch_in.setPlaceholderText("Paste Employee IDs here, one per line.\n"
                                         "Lines are used exactly as written (spaces count).")
        go = QPushButton("Validate all")
        go.setObjectName("PrimaryButton")
        go.clicked.connect(self.run_batch)
        self.batch_stats = QLabel()
        self.batch_stats.setObjectName("Muted")
        self.batch_out = _table(["#", "Input", "Verdict", "Final state", "Reason"])
        a11y(self.batch_out, "Batch validation results")
        a11y(self.batch_in, "Batch input", "One Employee ID per line, used exactly as written")
        batch_page = QWidget()
        bl = QVBoxLayout(batch_page)
        bl.setContentsMargins(0, 12, 0, 0)
        bl.addWidget(self.batch_in, 1)
        row = QHBoxLayout()
        row.addWidget(go)
        row.addWidget(self.batch_stats, 1)
        bl.addLayout(row)
        bl.addWidget(self.batch_out, 2)

        tabs = QTabWidget()
        tabs.addTab(suite_page, f"Test suite ({len(MASTER_TEST_SUITE)})")
        tabs.addTab(batch_page, "Batch")
        lay = QVBoxLayout(self)
        lay.setContentsMargins(24, 14, 24, 14)
        lay.addWidget(tabs)
        self.run_suite()

    def run_suite(self) -> None:
        passed = agree = 0
        for row, tc in enumerate(MASTER_TEST_SUITE):
            verdicts = {m: self._service.validate(tc.input_str, m) for m in _MODES}
            actual = verdicts["DFA"].accepted
            ok = actual == tc.expected_accepted
            same = len({v.accepted for v in verdicts.values()}) == 1
            passed += ok
            agree += same
            vals = [tc.id, tc.category, _shown(tc.input_str), "ACCEPTED" if tc.expected_accepted else "REJECTED",
                    "ACCEPTED" if actual else "REJECTED", "PASS" if ok else "FAIL", "yes" if same else "NO",
                    tc.expected_reason]
            for col, text in enumerate(vals):
                color = (P["ok"] if ok else P["bad"]) if col == 5 else (None if same or col != 6 else P["bad"])
                self.suite.setItem(row, col, _cell(text, color, center=col in (3, 4, 5, 6)))
            btn = QPushButton("Simulate")
            btn.setObjectName("ToolButton")
            btn.clicked.connect(lambda _=False, s=tc.input_str: self.simulateRequested.emit(s))
            self.suite.setCellWidget(row, 8, btn)
        total = len(MASTER_TEST_SUITE)
        self.stats.setText(f"{passed} / {total} passed · NFA, DFA and minimal DFA agree on {agree} / {total} inputs")

    def run_batch(self) -> None:
        lines = self.batch_in.toPlainText().split("\n")
        if lines and lines[-1] == "":
            lines.pop()
        self.batch_out.setRowCount(len(lines))
        accepted = 0
        for i, line in enumerate(lines):
            r = self._service.validate(line, "DFA")
            accepted += r.accepted
            vals = [str(i + 1), _shown(line), "ACCEPTED" if r.accepted else "REJECTED", r.final_state or "—", r.explanation]
            for col, text in enumerate(vals):
                self.batch_out.setItem(i, col, _cell(text, (P["ok"] if r.accepted else P["bad"]) if col == 2 else None))
        self.batch_stats.setText(f"{len(lines)} inputs · {accepted} accepted · {len(lines) - accepted} rejected")
