import sys

from PySide6.QtWidgets import QApplication

from app.gui.main_window import MainWindow
from app.gui.mock_services.services import MockAutomataService

def _load_stylesheet(app: QApplication) -> None:
    try:
        with open("app/gui/styles/theme.qss", "r", encoding="utf-8") as f:
            app.setStyleSheet(f.read())
    except FileNotFoundError:
        pass

def main() -> None:
    app = QApplication(sys.argv)
    _load_stylesheet(app)

    service = MockAutomataService()
    window = MainWindow(service)
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()