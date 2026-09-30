import os

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
pytest.importorskip("PySide6.QtWidgets")


@pytest.fixture(scope="session")
def qapp():
    from PySide6.QtWidgets import QApplication

    from app.gui.theme import load_fonts, load_stylesheet
    app = QApplication.instance() or QApplication([])
    load_fonts()
    app.setStyleSheet(load_stylesheet())
    return app


@pytest.fixture
def window(qapp):
    from app.gui.main_window import MainWindow
    from app.services.simulation_service import SimulationService
    w = MainWindow(SimulationService())
    w.show()
    yield w
    w.close()
