import sys

from PySide6.QtWidgets import QApplication

from app.gui.main_window import MainWindow
from app.gui.theme import load_fonts, load_stylesheet
from app.services.simulation_service import SimulationService


def main() -> None:
    app = QApplication(sys.argv)
    load_fonts()
    app.setStyleSheet(load_stylesheet())
    window = MainWindow(SimulationService())
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
