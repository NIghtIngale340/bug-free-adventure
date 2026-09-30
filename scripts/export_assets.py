"""
Export the three automaton diagrams and page screenshots to assets/ (offscreen Qt, no display needed).

    python scripts/export_assets.py
"""

import os
import sys
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from PySide6.QtCore import QEventLoop, QTimer  # noqa: E402
from PySide6.QtWidgets import QApplication  # noqa: E402

from app.core.pipeline import get_pipeline  # noqa: E402
from app.core.present import pipeline_graphs  # noqa: E402
from app.gui.main_window import MainWindow  # noqa: E402
from app.gui.theme import load_fonts, load_stylesheet  # noqa: E402
from app.gui.widgets.automaton_diagram import DiagramPanel  # noqa: E402
from app.services.simulation_service import SimulationService  # noqa: E402


def settle(ms: int = 350) -> None:   # long enough for the 180 ms transitions
    loop = QEventLoop()
    QTimer.singleShot(ms, loop.quit)
    loop.exec()


def main() -> None:
    app = QApplication(sys.argv)
    load_fonts()
    app.setStyleSheet(load_stylesheet())
    diagrams, shots = ROOT / "assets" / "diagrams", ROOT / "assets" / "screenshots"
    diagrams.mkdir(parents=True, exist_ok=True)
    shots.mkdir(parents=True, exist_ok=True)

    names = {"NFA": "nfa.png", "SUBSET": "dfa_subset_construction.png", "DFA": "dfa_minimal.png"}
    for mode, graph in pipeline_graphs(get_pipeline()).items():
        panel = DiagramPanel()
        panel.resize(1500, 640)
        panel.set_graph(graph)
        panel.show()
        settle()
        panel.view.grab().save(str(diagrams / names[mode]))

    w = MainWindow(SimulationService())
    w.resize(1240, 800)
    w.show()
    settle()
    sim = w.simulate

    def shot(name: str) -> None:
        settle()
        w.grab().save(str(shots / name))

    sim.load("EMP-2026-0042")
    for _ in range(6):
        sim.step_forward()
    shot("01_simulate_running.png")
    sim.run_all()
    shot("02_simulate_accepted.png")
    sim.load("EMP2026-0001")
    sim.run_all()
    shot("03_simulate_rejected_dead_state.png")
    sim.load("EMP-2026-12A4")
    shot("04_simulate_rejected_symbol_not_in_sigma.png")
    sim.model.setCurrentIndex(2)
    sim.load("EMP-2026-0042")
    for _ in range(9):
        sim.step_forward()
    shot("05_simulate_nfa_subsets.png")
    sim.model.setCurrentIndex(0)
    w.show_page(1)
    for i in range(w.theory.tabs.count()):
        w.theory.tabs.setCurrentIndex(i)
        shot(f"06_theory_{i + 1}_{w.theory.tabs.tabText(i).lower().replace(' ', '_').replace('ε-', 'e_')}.png")
    w.show_page(2)
    shot("07_tests.png")
    print("wrote", len(list(diagrams.glob('*.png'))), "diagrams and", len(list(shots.glob('*.png'))), "screenshots")


if __name__ == "__main__":
    main()
