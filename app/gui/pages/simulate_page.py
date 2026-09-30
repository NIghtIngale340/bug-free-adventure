from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QColor, QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QAbstractButton,
    QApplication,
    QComboBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QPushButton,
    QSlider,
    QSplitter,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from app.core.language import validate_symbols
from app.core.present import pipeline_graphs
from app.data.id_rules import ID_SEGMENTS
from app.gui.a11y import label as a11y
from app.gui.theme import PALETTE
from app.gui.widgets.automaton_diagram import DiagramPanel
from app.gui.widgets.tape_view import TapeView, segment_legend
from app.gui.widgets.verdict_banner import VerdictBanner

_MODELS = [
    ("Minimal DFA (authoritative)", "DFA"),
    ("DFA before minimization (subset construction)", "SUBSET"),
    ("ε-NFA (Thompson, from the RE)", "NFA"),
]
_EXAMPLES = [
    ("Examples…", None),
    ("Valid — EMP-2026-0042", "EMP-2026-0042"),
    ("Valid — EMP-2099-9999", "EMP-2099-9999"),
    ("Symbol not in Σ — EMP-2026-12A4", "EMP-2026-12A4"),
    ("Missing hyphen — EMP2026-0001", "EMP2026-0001"),
    ("Year too short — EMP-26-0001", "EMP-26-0001"),
    ("Wrong prefix — AXP-2026-0001", "AXP-2026-0001"),
    ("Too short — EMP-2026-123", "EMP-2026-123"),
    ("Too long — EMP-2026-00001", "EMP-2026-00001"),
    ("Trailing space — 'EMP-2026-0001 '", "EMP-2026-0001 "),
]


class SimulatePage(QWidget):
    """Enter an ID → Layer 1 alphabet check → run the automaton symbol by symbol → verdict.

    Loading never starts the run: the presenter chooses Step, Play or Run all. The input text is
    used exactly as typed (no trimming) so the GUI and the validator always agree.
    """

    resultReady = Signal(object)

    def __init__(self, service, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._service = service
        self._graphs = pipeline_graphs(service.get_pipeline())
        self._session: str | None = None
        self._text = ""
        self._mode = "DFA"
        self._prev: frozenset[str] = frozenset()
        self._steps: list = []
        self._loaded_mode: str | None = None

        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)

        # --- input row
        self.input = QLineEdit()
        self.input.setObjectName("IdInput")
        self.input.setPlaceholderText("EMP-2026-0042")
        self.input.setMaxLength(64)
        self.input.returnPressed.connect(self.load_from_input)
        load = self.btn_load = QPushButton("Load")
        load.setObjectName("PrimaryButton")
        load.setFocusPolicy(Qt.FocusPolicy.TabFocus)
        load.clicked.connect(self.load_from_input)
        self.examples = QComboBox()
        for label, value in _EXAMPLES:
            self.examples.addItem(label, value)
        self.examples.activated.connect(self._example_chosen)
        self.model = QComboBox()
        for label, value in _MODELS:
            self.model.addItem(label, value)
        self.model.currentIndexChanged.connect(self._model_changed)
        top = QHBoxLayout()
        top.setSpacing(8)
        top.addWidget(self.input, 1)
        top.addWidget(load)
        top.addWidget(self.examples)
        top.addWidget(QLabel("Model"))
        top.addWidget(self.model)

        # --- tape + live readout
        self.tape = TapeView()
        self.legend = QLabel(segment_legend(ID_SEGMENTS))
        self.legend.setObjectName("Muted")
        self.legend.setTextFormat(Qt.TextFormat.RichText)
        self.symbol_label = QLabel()
        self.state_label = QLabel()
        self.formula = QLabel()
        self.formula.setObjectName("Mono")
        info = QHBoxLayout()
        info.addWidget(self.symbol_label)
        info.addSpacing(18)
        info.addWidget(self.state_label)
        info.addSpacing(18)
        info.addWidget(self.formula, 1)

        self.banner = VerdictBanner()

        # --- diagram | history
        self.diagram = DiagramPanel()
        self.history = QTableWidget(0, 5)
        self.history.setHorizontalHeaderLabels(["#", "Symbol", "From", "To", "Result"])
        self.history.verticalHeader().setVisible(False)
        self.history.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.history.setSelectionMode(QTableWidget.SelectionMode.NoSelection)
        hh = self.history.horizontalHeader()
        hh.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        hh.setStretchLastSection(True)
        hist_title = QLabel("Transition history")
        hist_title.setObjectName("SubHeading")
        right = QWidget()
        rl = QVBoxLayout(right)
        rl.setContentsMargins(12, 0, 0, 0)
        rl.addWidget(hist_title)
        rl.addWidget(self.history, 1)
        split = QSplitter(Qt.Orientation.Horizontal)
        split.addWidget(self.diagram)
        split.addWidget(right)
        split.setStretchFactor(0, 3)
        split.setStretchFactor(1, 2)
        split.setChildrenCollapsible(False)
        split.setSizes([720, 420])

        # --- controls
        self.btn_prev = self._button("Prev", self.step_back, "Previous step (←)")
        self.btn_play = self._button("Play", self.toggle_play, "Play / pause (Space)")
        self.btn_step = self._button("Step", self.step_forward, "Consume one symbol (→)")
        self.btn_all = self._button("Run all", self.run_all, "Finish the run")
        self.btn_reset = self._button("Reset", self.reset, "Back to the start state (Ctrl+R)")
        self.speed = QSlider(Qt.Orientation.Horizontal)
        self.speed.setRange(5, 40)          # 0.5x .. 4.0x
        self.speed.setValue(10)
        self.speed.setFixedWidth(120)
        self.speed.valueChanged.connect(self._speed_changed)
        self.speed_label = QLabel()
        self.speed_label.setObjectName("Muted")
        controls = QHBoxLayout()
        for b in (self.btn_prev, self.btn_play, self.btn_step, self.btn_all, self.btn_reset):
            controls.addWidget(b)
        controls.addStretch()
        controls.addWidget(QLabel("Speed"))
        controls.addWidget(self.speed)
        controls.addWidget(self.speed_label)

        lay = QVBoxLayout(self)
        lay.setContentsMargins(24, 12, 24, 12)
        lay.setSpacing(7)
        lay.addLayout(top)
        lay.addWidget(self.tape)
        lay.addWidget(self.legend)
        lay.addLayout(info)
        lay.addWidget(self.banner)
        lay.addWidget(split, 1)
        lay.addLayout(controls)

        for key, fn in ((Qt.Key.Key_Space, self._space), (Qt.Key.Key_Right, self.step_forward),
                        (Qt.Key.Key_Left, self.step_back)):
            QShortcut(QKeySequence(key), self, activated=fn, context=Qt.ShortcutContext.WidgetWithChildrenShortcut)
        QShortcut(QKeySequence("Ctrl+R"), self, activated=self.reset,
                  context=Qt.ShortcutContext.WidgetWithChildrenShortcut)

        a11y(self.input, "Employee ID", "Type an ID and press Enter to load it. The text is used exactly as typed.")
        a11y(load, "Load", "Load the typed ID and stop at the start state")
        a11y(self.examples, "Example inputs")
        a11y(self.model, "Automaton model", "Minimal DFA, DFA before minimization, or ε-NFA")
        a11y(self.history, "Transition history", "One row per symbol read")
        a11y(self.speed, "Playback speed")
        a11y(self.symbol_label, "Current symbol")
        a11y(self.state_label, "Current state")
        a11y(self.formula, "Transition function value")
        chain = [self.input, load, self.examples, self.model, self.btn_prev, self.btn_play, self.btn_step,
                 self.btn_all, self.btn_reset, self.speed, self.history]
        for a, b in zip(chain, chain[1:]):
            QWidget.setTabOrder(a, b)

        self._speed_changed(self.speed.value())
        self.diagram.set_graph(self._graphs["DFA"])
        self._loaded_mode = "DFA"
        self._sync_controls()

    def _button(self, text, slot, tip) -> QPushButton:
        b = QPushButton(text)
        b.setToolTip(tip)
        b.setAccessibleName(text)
        b.setAccessibleDescription(tip)
        b.setFocusPolicy(Qt.FocusPolicy.TabFocus)   # keyboard focus via Tab; mouse clicks never steal it
        b.clicked.connect(slot)
        return b

    def _space(self) -> None:
        """Space: activate the focused button (keyboard users), otherwise play / pause."""
        focused = QApplication.focusWidget()
        if isinstance(focused, QAbstractButton) and focused.isEnabled():
            focused.click()
        else:
            self.toggle_play()

    # --- loading ------------------------------------------------------------------------

    def load_from_input(self) -> None:
        self.load(self.input.text())

    def load(self, text: str) -> None:
        """Load `text` exactly as given (never trimmed) and stop at the start state."""
        self.input.setText(text)
        self._text = text
        self._mode = self.model.currentData()
        self._timer.stop()
        if self._session:
            self._service.close(self._session)
        self._session = self._service.create_session(text, self._mode)
        self._setup_view()

    def _setup_view(self) -> None:
        sid = self._session
        _, illegal = validate_symbols(self._text)
        self.tape.load(self._text, {i for i, _ in illegal}, ID_SEGMENTS)
        if self._loaded_mode != self._mode:
            self.diagram.set_graph(self._graphs[self._mode])
            self._loaded_mode = self._mode
        self._prev = self._service.active_states(sid)
        self.diagram.view.reset_highlight(self._prev)
        self.history.setRowCount(0)
        self._steps = []
        self.symbol_label.setText("Symbol: —")
        self.state_label.setText(f"State: {self._label(self._prev)}")
        self.formula.setText("")
        self.btn_play.setText("Play")
        if self._service.is_finished(sid):     # empty input or symbols outside Σ: nothing to run
            self._finish()
        else:
            self.banner.show_idle(
                f"Layer 1 passed: all {len(self._text)} symbols are in Σ. "
                f"The automaton is at its start state — press Step or Play.")
        self._sync_controls()

    # --- stepping -------------------------------------------------------------------------

    def step_forward(self) -> bool:
        """Consume one symbol. Returns False if the run was already finished."""
        if not self._session or self._service.is_finished(self._session):
            return False
        step = self._service.step(self._session)
        if step is None:
            return False
        self._apply(step)
        if self._service.is_finished(self._session):
            self._finish()
        else:
            self.banner.show_running(f"Read {step.step} of {len(self._text)} symbols.")
        self._sync_controls()
        return True

    def step_back(self) -> None:
        n = len(self._steps) - 1
        if n < 0 or not self._session:
            return
        self._timer.stop()
        self._service.reset(self._session)
        self._setup_view()
        for _ in range(n):
            self._apply(self._service.step(self._session))
        if n:
            self.banner.show_running(f"Read {n} of {len(self._text)} symbols.")
        self._sync_controls()

    def run_all(self) -> None:
        self._timer.stop()
        self.btn_play.setText("Play")
        while self.step_forward():
            pass

    def reset(self) -> None:
        if not self._session:
            return
        self._timer.stop()
        self._service.reset(self._session)
        self._setup_view()

    def toggle_play(self) -> None:
        if not self._session:
            return
        if self._timer.isActive():
            self._timer.stop()
            self.btn_play.setText("Play")
        else:
            if self._service.is_finished(self._session):
                self.reset()
                if self._service.is_finished(self._session):
                    return
            self._timer.start()
            self.btn_play.setText("Pause")

    def _tick(self) -> None:
        if not self.step_forward():
            self._timer.stop()
            self.btn_play.setText("Play")

    # --- rendering (single path used by Step / Play / Run all / Prev) ------------------------

    @staticmethod
    def _label(states) -> str:
        return "{" + ", ".join(sorted(states, key=lambda s: (len(s), s))) + "}" if len(states) != 1 else next(iter(states))

    def _apply(self, step) -> None:
        nxt = self._service.active_states(self._session)
        self._steps.append(step)
        self.tape.set_progress(step.step, failed=not step.is_valid)
        self.symbol_label.setText(f"Symbol: {step.symbol!r}  ({step.step} / {len(self._text)})")
        self.state_label.setText(f"State: {step.from_state} → {step.to_state}")
        self.formula.setText(
            f"δ({step.from_state}, {step.symbol}) = {step.to_state}" + ("   ✗ no transition" if not step.is_valid else ""))
        self.diagram.view.show_step(self._prev, nxt, step.symbol, dead=not step.is_valid)
        self._prev = nxt
        row = self.history.rowCount()
        self.history.insertRow(row)
        for col, text in enumerate((str(step.step), step.symbol, step.from_state, step.to_state,
                                    "ok" if step.is_valid else "dead")):
            item = QTableWidgetItem(text)
            if not step.is_valid:
                item.setForeground(Qt.GlobalColor.white)
                item.setBackground(QColor(PALETTE["bad_bg"]))
            self.history.setItem(row, col, item)
        self.history.scrollToBottom()

    def _finish(self) -> None:
        self._timer.stop()
        self.btn_play.setText("Play")
        result = self._service.result(self._session)
        self.banner.show_result(result)
        if result.accepted:
            self.tape.set_progress(len(self._text), accepted=True)
            self.diagram.view.show_final(True)
        elif self._steps:
            self.diagram.view.show_final(False)
        self.resultReady.emit(result)

    def _sync_controls(self) -> None:
        loaded = self._session is not None
        finished = loaded and self._service.is_finished(self._session)
        self.btn_prev.setEnabled(len(self._steps) > 0)
        self.btn_step.setEnabled(loaded and not finished)
        self.btn_all.setEnabled(loaded and not finished)
        self.btn_play.setEnabled(loaded and (not finished or len(self._steps) > 0))
        self.btn_reset.setEnabled(loaded)

    # --- small handlers -------------------------------------------------------------------------

    def _example_chosen(self, index: int) -> None:
        value = self.examples.itemData(index)
        if value is not None:
            self.load(value)
        self.examples.setCurrentIndex(0)

    def _model_changed(self) -> None:
        if self._session:
            self.load(self._text)
        else:
            self._mode = self.model.currentData()
            self.diagram.set_graph(self._graphs[self._mode])
            self._loaded_mode = self._mode

    def _speed_changed(self, value: int) -> None:
        factor = value / 10
        self._timer.setInterval(int(800 / factor))
        self.speed_label.setText(f"{factor:.1f}×")
