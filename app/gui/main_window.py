from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QButtonGroup,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from app.gui.pages.simulate_page import SimulatePage
from app.gui.pages.tests_page import TestsPage
from app.gui.pages.theory_page import TheoryPage


class MainWindow(QMainWindow):
    """Shell with three always-available views: Simulate · Theory · Tests."""

    def __init__(self, service) -> None:
        super().__init__()
        self.setWindowTitle("Employee ID Validator — CCAUTOMA")
        self.resize(1240, 730)
        self.setMinimumSize(1040, 660)

        self.simulate = SimulatePage(service)
        self.theory = TheoryPage(service)
        self.tests = TestsPage(service)
        self.simulate.resultReady.connect(self.theory.set_last_result)
        self.tests.simulateRequested.connect(self._simulate_this)

        self.stack = QStackedWidget()
        header = QWidget()
        header.setObjectName("AppHeader")
        row = QHBoxLayout(header)
        row.setContentsMargins(24, 0, 24, 0)
        title = QLabel("Employee ID Validator")
        title.setObjectName("AppTitle")
        sub = QLabel("EMP-YYYY-NNNN · RE → NFA → DFA → minimal DFA")
        sub.setObjectName("AppSub")
        row.addWidget(title)
        row.addSpacing(12)
        row.addWidget(sub)
        row.addStretch()
        group = QButtonGroup(self)
        self.nav: list[QPushButton] = []
        for i, (name, page) in enumerate((("Simulate", self.simulate), ("Theory", self.theory), ("Tests", self.tests))):
            b = QPushButton(name)
            b.setObjectName("NavButton")
            b.setCheckable(True)
            b.setFocusPolicy(Qt.FocusPolicy.TabFocus)
            b.setAccessibleName(f"{name} view")
            b.clicked.connect(lambda _=False, idx=i: self.show_page(idx))
            group.addButton(b)
            row.addWidget(b)
            self.nav.append(b)
            self.stack.addWidget(page)

        central = QWidget()
        lay = QVBoxLayout(central)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)
        lay.addWidget(header)
        lay.addWidget(self.stack, 1)
        self.setCentralWidget(central)
        self.show_page(0)

    def show_page(self, index: int) -> None:
        self.stack.setCurrentIndex(index)
        self.nav[index].setChecked(True)
        if index == 0:
            self.simulate.input.setFocus()

    def _simulate_this(self, text: str) -> None:
        self.show_page(0)
        self.simulate.load(text)
