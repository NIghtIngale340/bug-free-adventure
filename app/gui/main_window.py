from PySide6.QtCore import QEvent
from PySide6.QtWidgets import QMainWindow, QStackedWidget

from app.gui.pages.landing_page import LandingPage
from app.gui.pages.simulator_page import SimulatorPage
from app.gui.pages.automata_page import AutomataPage
from app.gui.pages.test_cases_page import TestCasesPage


class MainWindow(QMainWindow):
    """Application shell: Landing Page <-> Simulator Page <-> Automata Page <-> Test Cases Page."""

    def __init__(self, automata_service) -> None:
        super().__init__()
        self.setWindowTitle("Employee ID Validator — CCAUTOMA")
        self.resize(1050, 750)
        self.setMinimumSize(850, 600)

        metadata = automata_service.get_metadata()
        accepting_states = set(metadata.accepting_states)

        self._stack = QStackedWidget()
        self.setCentralWidget(self._stack)

        self._landing_page = LandingPage(
            on_submit=self._go_to_simulator,
            on_open_test_cases=self._go_to_test_cases,
        )
        self._simulator_page = SimulatorPage(
            automata_service, accepting_states,
            on_check_another=self._go_to_landing,
            on_view_automata=self._go_to_automata,
            on_view_tests=self._go_to_test_cases,
        )
        self._automata_page = AutomataPage(
            automata_service,
            on_check_another=self._go_to_landing,
            on_back_to_simulator=self._go_to_simulator_page,
            on_view_tests=self._go_to_test_cases,
        )
        self._test_cases_page = TestCasesPage(
            automata_service,
            on_select_test=self._go_to_simulator,
            on_back=self._go_to_landing,
        )

        self._stack.addWidget(self._landing_page)
        self._stack.addWidget(self._simulator_page)
        self._stack.addWidget(self._automata_page)
        self._stack.addWidget(self._test_cases_page)
        self._stack.setCurrentWidget(self._landing_page)

    def _go_to_simulator(self, input_string: str) -> None:
        self._stack.setCurrentWidget(self._simulator_page)
        self._simulator_page.load_and_run(input_string)

    def _go_to_simulator_page(self) -> None:
        """Return to the simulator page WITHOUT re-running the simulation."""
        self._stack.setCurrentWidget(self._simulator_page)

    def _go_to_automata(self) -> None:
        self._automata_page.refresh(self._simulator_page.get_last_result())
        self._stack.setCurrentWidget(self._automata_page)

    def _go_to_test_cases(self) -> None:
        self._test_cases_page.run_all_tests()
        self._stack.setCurrentWidget(self._test_cases_page)

    def _go_to_landing(self) -> None:
        self._landing_page.clear()
        self._stack.setCurrentWidget(self._landing_page)

    def changeEvent(self, event) -> None:
        super().changeEvent(event)
        if event.type() in (QEvent.Type.ActivationChange, QEvent.Type.WindowStateChange):
            if self.isActiveWindow():
                self.update()
                self._stack.currentWidget().update()
                self._simulator_page.refresh_view()