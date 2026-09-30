import re

from PySide6.QtCore import Qt
from PySide6.QtGui import QBrush, QColor
from PySide6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QPushButton,
    QSlider,
    QSplitter,
    QTableWidget,
    QTableWidgetItem,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from app.core.equivalence import dfa_equivalent, exhaustive_agreement
from app.core.pipeline import reference_dfa
from app.core.present import (
    SUBSET_HEADERS,
    block_text,
    compress_symbols,
    distance_rows,
    grouped_table,
    pipeline_graphs,
    report_md,
    tuple_lines,
)
from app.core.simulator import format_subset
from app.data.id_rules import ALPHABET, ID_SEGMENTS, RE_PATTERN
from app.data.test_cases import MASTER_TEST_SUITE
from app.gui.a11y import label as a11y
from app.gui.theme import PALETTE as P
from app.gui.widgets.automaton_diagram import DiagramPanel
from app.gui.widgets.tape_view import TapeView, segment_legend


def _label(text: str, role: str = "", wrap: bool = True) -> QLabel:
    w = QLabel(text)
    if role:
        w.setObjectName(role)
    w.setWordWrap(wrap)
    w.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
    return w


def _table(headers: list[str], rows: list[list[str]], stretch_last: bool = True, name: str = "") -> QTableWidget:
    t = QTableWidget(len(rows), len(headers))
    a11y(t, name or "Table: " + ", ".join(headers))
    t.setHorizontalHeaderLabels(headers)
    t.verticalHeader().setVisible(False)
    t.verticalHeader().setDefaultSectionSize(26)
    t.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
    for r, row in enumerate(rows):
        for c, text in enumerate(row):
            t.setItem(r, c, QTableWidgetItem(str(text)))
    hh = t.horizontalHeader()
    hh.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
    hh.setStretchLastSection(stretch_last)
    return t


def _column(*widgets, margins=(0, 0, 0, 0)) -> QWidget:
    w = QWidget()
    lay = QVBoxLayout(w)
    lay.setContentsMargins(*margins)
    lay.setSpacing(8)
    for x in widgets:
        lay.addWidget(x, 1 if isinstance(x, (QTableWidget, DiagramPanel, QSplitter)) else 0)
    return w


def _split(left: QWidget, right: QWidget, sizes=(1, 1)) -> QSplitter:
    s = QSplitter(Qt.Orientation.Horizontal)
    s.addWidget(left)
    s.addWidget(right)
    s.setChildrenCollapsible(False)
    s.setStretchFactor(0, sizes[0])
    s.setStretchFactor(1, sizes[1])
    return s


def _pad(w: QWidget) -> QWidget:
    holder = QWidget()
    lay = QVBoxLayout(holder)
    lay.setContentsMargins(20, 14, 20, 14)
    lay.addWidget(w)
    return holder


def _shown(s: str) -> str:
    return "(empty)" if s == "" else (repr(s) if s != s.strip() else s)


class TheoryPage(QWidget):
    """Every stage of RE → NFA → DFA → minimal DFA, computed from the objects the simulator runs."""

    def __init__(self, service, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._p = service.get_pipeline()
        self._graphs = pipeline_graphs(self._p)
        self._last = None

        title = _label("Automata theory", "Heading", wrap=False)
        sub = _label("Each tab is generated from the same objects the simulator executes.", "Muted", wrap=False)
        copy = QPushButton("Copy report (Markdown)")
        copy.setFocusPolicy(Qt.FocusPolicy.TabFocus)
        copy.clicked.connect(lambda: self._copy(copy))
        head = QHBoxLayout()
        head.addWidget(title)
        head.addSpacing(12)
        head.addWidget(sub)
        head.addStretch()
        head.addWidget(copy)

        d = self._p.min_dfa
        chips = QHBoxLayout()
        for text, tip in (
            (f"Σ = {len(d.alphabet)} symbols", "Alphabet Σ: the finite set of symbols an ID may contain — E, M, P, '-' and 0–9."),
            (f"Q = {len(d.states)} states", "States Q: q0…q13 count how much of a valid ID has been matched; q_trap is the dead state."),
            (f"q₀ = {d.start_state}", "Start state: nothing read yet; the only way forward is 'E'."),
            (f"F = {{{', '.join(sorted(d.accepting_states))}}}", "Accepting states F: a complete, well-formed ID has been read."),
            ("δ : Q × Σ → Q", "Transition function: exactly one next state for every (state, symbol). Undefined moves go to q_trap."),
        ):
            chip = QLabel(text)
            chip.setObjectName("Chip")
            chip.setToolTip(tip)
            chips.addWidget(chip)
        chips.addStretch()

        self.tabs = QTabWidget()
        for name, builder in (("Language", self._language), ("Regular expression", self._regex),
                              ("ε-NFA", self._nfa), ("Subset construction", self._subset),
                              ("DFA", self._dfa), ("Minimization", self._minimization),
                              ("Minimal DFA", self._min_dfa), ("Equivalence", self._equivalence)):
            self.tabs.addTab(builder(), name)

        lay = QVBoxLayout(self)
        lay.setContentsMargins(24, 14, 24, 10)
        lay.setSpacing(8)
        lay.addLayout(head)
        lay.addLayout(chips)
        lay.addWidget(self.tabs, 1)

    # --- tabs ------------------------------------------------------------------------------------

    def _language(self) -> QWidget:
        accepted = [[_shown(t.input_str), t.expected_reason] for t in MASTER_TEST_SUITE if t.expected_accepted][:10]
        rejected = [[_shown(t.input_str), t.expected_reason] for t in MASTER_TEST_SUITE if not t.expected_accepted]
        sigma = ", ".join(sorted(ALPHABET, key=lambda c: (c.isdigit(), c != "-", c)))
        text = _column(
            _label("Problem", "SubHeading"),
            _label("An organization issues employee IDs of the form EMP-YYYY-NNNN. The validator, used by HR staff "
                   "who type IDs by hand, decides whether a string belongs to that language and shows how the "
                   "automaton reached its decision."),
            _label("Input / valid / invalid", "SubHeading"),
            _label("Input: any string the user types (any characters, any length). Valid: the string is in L. "
                   "Invalid: everything else — including strings with characters outside Σ."),
            _label("Why a finite automaton", "SubHeading"),
            _label("Every word in L has length exactly 13 and L is finite (10⁸ IDs); checking it needs no unbounded "
                   "memory, no counter and no stack, so L is regular and a DFA recognizes it."),
            _label(f"Σ = {{{sigma}}}     (|Σ| = {len(ALPHABET)})\nL = {{ w ∈ Σ* | w = EMP-d₁d₂d₃d₄-d₅d₆d₇d₈, dᵢ ∈ 0–9 }}", "MonoBlock"),
        )
        tables = _split(_column(_label("Accepted (10)", "SubHeading"), _table(["String", "Note"], accepted)),
                        _column(_label(f"Rejected ({len(rejected)})", "SubHeading"), _table(["String", "Reason"], rejected)))
        return _pad(_column(text, tables))

    def _regex(self) -> QWidget:
        p = self._p
        parts = [["1–3", "EMP", "fixed uppercase prefix E·M·P", "EMP"],
                 ["4", "-", "first separator", "-"],
                 ["5–8", "D⁴", "exactly four digits: the year YYYY (any four digits — syntax only)", "2026"],
                 ["9", "-", "second separator", "-"],
                 ["10–13", "D⁴", "exactly four digits: the employee number NNNN", "0042"]]
        why = [[_shown(t.input_str), t.expected_reason] for t in MASTER_TEST_SUITE if not t.expected_accepted][:8]
        defs = "   ".join(f"{k} = {v}" for k, v in p.regex_definitions.items())
        demo = TapeView()
        demo.load("EMP-2026-0042", segments=ID_SEGMENTS)
        demo_legend = _label(segment_legend(ID_SEGMENTS), "Muted")
        demo_legend.setTextFormat(Qt.TextFormat.RichText)
        return _pad(_column(
            _label("Formal regular expression", "SubHeading"),
            _label(p.regex_formal, "BigMono", wrap=False),
            demo, demo_legend,
            _label(f"{p.regex_expanded}      where  {defs}", "MonoBlock"),
            _label("Union (∪), concatenation (·) and bounded repetition (superscript) are the only operators. "
                   f"Python check pattern (test oracle only, never used for acceptance): {RE_PATTERN}  with re.fullmatch.", "Muted"),
            _label("Components", "SubHeading"),
            self._fixed_rows(_table(["Position", "Component", "Meaning", "Example"], parts)),
            _label("Why these strings do not match", "SubHeading"),
            _table(["String", "Reason"], why),
        ))

    @staticmethod
    def _fixed_rows(t: QTableWidget) -> QTableWidget:
        t.setFixedHeight(t.horizontalHeader().height() + 26 * t.rowCount() + 6)
        return t

    def _nfa(self) -> QWidget:
        p = self._p
        t = grouped_table(p.nfa)
        left = _column(
            _label("\n".join(tuple_lines("M_NFA", p.nfa)), "MonoBlock"),
            _label("Thompson construction: each of the 13 symbols becomes an atom of two states (a digit atom has "
                   f"10 parallel edges); {p.nfa.epsilon_edge_count} ε-edges glue the atoms together. → marks the start state, "
                   "* the accepting state. A missing move means ∅ — an NFA has no trap state.", "Muted"),
            _table(t.headers, t.rows))
        panel = DiagramPanel()
        panel.set_graph(self._graphs["NFA"])
        return _pad(_split(left, panel, (1, 1)))

    def _subset(self) -> QWidget:
        steps = self._p.subset_steps
        self._steps = steps
        master = _table(["DFA state", "NFA subset", "Accepting"],
                        [[s.name, format_subset(s.subset), "yes" if s.accepting else ""] for s in steps])
        master.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        master.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self._detail_title = _label("", "SubHeading")
        self._detail_holder = QWidget()
        self._detail_lay = QVBoxLayout(self._detail_holder)
        self._detail_lay.setContentsMargins(0, 0, 0, 0)
        master.itemSelectionChanged.connect(lambda: self._show_subset(master.currentRow()))
        algo = _label("Start subset = ε-closure({n0}).  For every symbol a: move(S, a), then ε-closure. "
                      "Each new subset becomes a DFA state; the empty subset is the dead state D_trap. "
                      "Symbols with the same outcome are grouped. Select a DFA state to see its computation.", "Muted")
        right = _column(algo, self._detail_title, self._detail_holder)
        master.selectRow(1)
        return _pad(_split(_column(_label("Reachable subsets", "SubHeading"), master), right, (2, 3)))

    def _show_subset(self, row: int) -> None:
        if not 0 <= row < len(self._steps):
            return
        st = self._steps[row]
        self._detail_title.setText(f"{st.name} = {format_subset(st.subset)}" + ("   (accepting)" if st.accepting else ""))
        while self._detail_lay.count():
            self._detail_lay.takeAt(0).widget().deleteLater()
        rows = [[compress_symbols(m.symbols), format_subset(m.move), format_subset(m.closure), m.target] for m in st.moves]
        self._detail_lay.addWidget(_table(SUBSET_HEADERS[2:], rows))

    def _dfa(self) -> QWidget:
        p = self._p
        t = grouped_table(p.subset_dfa)
        left = _column(_label("\n".join(tuple_lines("M_DFA", p.subset_dfa)), "MonoBlock"),
                       _label("δ is total: undefined moves lead to D_trap (shown in every empty cell). "
                              "The column 0–9 stands for ten identical columns.", "Muted"),
                       _table(t.headers, t.rows))
        panel = DiagramPanel()
        panel.set_graph(self._graphs["SUBSET"])
        return _pad(_split(left, panel, (1, 1)))

    def _minimization(self) -> QWidget:
        m = self._p.minimization
        self._rounds = m.rounds
        merged = ", ".join(block_text(g) for g in m.merged_groups) or "none — the DFA is already minimal"
        summary = _label(
            f"1. Unreachable states removed: {', '.join(m.removed_unreachable) or 'none'}\n"
            "2. P₀ = { F, Q ∖ F } (accepting vs. non-accepting)\n"
            f"3. Refinement: split a block when its members go to different blocks on some symbol — "
            f"stable after {len(m.rounds) - 1} rounds\n"
            f"4. Merged groups: {merged}   ({m.states_before} → {m.states_after} states)", "MonoBlock")
        self._min_summary = summary
        self._round_label = _label("", "SubHeading")
        slider = QSlider(Qt.Orientation.Horizontal)
        slider.setRange(0, len(m.rounds) - 1)
        slider.setValue(len(m.rounds) - 1)
        self._partition_holder = QWidget()
        self._partition_lay = QVBoxLayout(self._partition_holder)
        self._partition_lay.setContentsMargins(0, 0, 0, 0)
        slider.valueChanged.connect(self._show_round)
        left = _column(summary, _label("Drag the slider to replay the refinement rounds P₀ … P" + str(len(m.rounds) - 1), "Muted"),
                       self._round_label, slider, self._partition_holder)
        need = dict(distance_rows(m.dfa))
        mapping = [[o, n, need[n], "merged" if any(o in g for g in m.merged_groups) else "kept"]
                   for o, n in m.state_map.items()]
        right = _column(
            _label("Why nothing merges", "SubHeading"),
            _label("Every live state needs a different number of further symbols to reach acceptance, so no two "
                   "are equivalent; q_trap can never accept. Each refinement round isolates exactly one more state.", "Muted"),
            _table(["Original", "Minimized", "Fewest symbols to accept", "Fate"], mapping))
        self._show_round(len(m.rounds) - 1)
        return _pad(_split(left, right))

    def _show_round(self, k: int) -> None:
        part = self._rounds[k]
        prev = {b for b in self._rounds[k - 1]} if k else set()
        self._round_label.setText(f"Partition P{k}   ({len(part)} blocks)" + ("   — initial partition {F, Q∖F}" if k == 0 else ""))
        while self._partition_lay.count():
            self._partition_lay.takeAt(0).widget().deleteLater()
        rows = [[str(i + 1), str(len(b)), block_text(b, 6), "new" if k and b not in prev else ""] for i, b in enumerate(part)]
        self._partition_lay.addWidget(_table(["Block", "Size", "Members", ""], rows))

    def _min_dfa(self) -> QWidget:
        d = self._p.min_dfa
        self._min_tab = grouped_table(d)
        self._min_table = _table(self._min_tab.headers, self._min_tab.rows)
        left = _column(_label("\n".join(tuple_lines("M_min", d)), "MonoBlock"),
                       _label("Coloured cells trace the last run on this automaton "
                              "(amber = used, green = final accepted step, red = fell into q_trap).", "Muted"),
                       self._min_table)
        panel = DiagramPanel()
        panel.set_graph(self._graphs["DFA"])
        return _pad(_split(left, panel, (1, 1)))

    def _equivalence(self) -> QWidget:
        p = self._p
        ref = dfa_equivalent(p.min_dfa, reference_dfa())
        yes = lambda e: f"EQUAL — {e.pairs_explored} state pairs explored, no distinguishing word"   # noqa: E731
        self._eq_rows = [
            ["Subset DFA ≡ minimal DFA", "Product automaton, exhaustive BFS", yes(p.equivalence) if p.equivalence.equal else f"DIFFERENT: {p.equivalence.counterexample!r}"],
            ["Minimal DFA ≡ hand-written reference table", "Product automaton (reference is used only for this check)", yes(ref) if ref.equal else f"DIFFERENT: {ref.counterexample!r}"],
            ["ε-NFA ≡ DFA", "Subset construction preserves the language; sampled exhaustively below", "not run yet"],
            ["RE ≡ ε-NFA", "Thompson construction preserves the language; PCRE oracle below", "not run yet"],
        ]
        self._eq_table = self._fixed_rows(_table(["Claim", "Method", "Result"], self._eq_rows))
        run = QPushButton("Run exhaustive check")
        run.setObjectName("PrimaryButton")
        run.setFocusPolicy(Qt.FocusPolicy.TabFocus)
        run.clicked.connect(self._run_exhaustive)
        self._eq_out = _label("", "MonoBlock")
        return _pad(_column(
            _label("Do RE, NFA, DFA and minimal DFA recognize the same language?", "SubHeading"),
            self._eq_table,
            _label("Exhaustive check: every word over Σ up to length 4 (41,371 words) is run through the NFA, the "
                   "subset DFA, the minimal DFA and the PCRE oracle; any disagreement is counted.", "Muted"),
            run, self._eq_out, QWidget()))

    def _run_exhaustive(self) -> None:
        p = self._p
        oracle = re.compile(RE_PATTERN)
        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        try:
            total, bad = exhaustive_agreement(
                {"ε-NFA": p.nfa.accepts, "subset DFA": p.subset_dfa.accepts, "minimal DFA": p.min_dfa.accepts},
                lambda w: oracle.fullmatch(w) is not None, ALPHABET, 4)
        finally:
            QApplication.restoreOverrideCursor()
        self._eq_out.setText(f"{total:,} words checked. Disagreements with the oracle — "
                             + ", ".join(f"{k}: {v}" for k, v in bad.items()))
        ok = not any(bad.values())
        for row, res in ((2, bad["ε-NFA"] == bad["subset DFA"] == 0), (3, bad["ε-NFA"] == 0)):
            self._eq_table.setItem(row, 2, QTableWidgetItem(
                f"EQUAL on all {total:,} words" if ok and res else "DISAGREEMENT — see below"))

    # --- integration ---------------------------------------------------------------------------------

    def set_last_result(self, result) -> None:
        """Colour the path of the last run in the minimal-DFA table."""
        self._last = result
        t, states = self._min_table, self._p.min_dfa.states
        for r in range(t.rowCount()):
            for c in range(t.columnCount()):
                t.item(r, c).setBackground(QBrush())
        for i, step in enumerate(result.trace):
            if step.from_state not in states or step.symbol not in self._min_tab.col_of:
                continue
            item = t.item(states.index(step.from_state), self._min_tab.col_of[step.symbol])
            last_ok = result.accepted and i == len(result.trace) - 1
            item.setBackground(QColor(P["bad_bg"] if not step.is_valid else P["ok_bg"] if last_ok else P["accent_bg"]))

    def _copy(self, button: QPushButton) -> None:
        QApplication.clipboard().setText(report_md(self._p, self._last))
        button.setText("Copied to clipboard")
        from PySide6.QtCore import QTimer
        QTimer.singleShot(2000, lambda: button.setText("Copy report (Markdown)"))
