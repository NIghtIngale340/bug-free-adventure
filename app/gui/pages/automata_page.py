from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame,
    QScrollArea, QTableWidget, QTableWidgetItem, QHeaderView, QSizePolicy,
)

_USED_COLOR = QColor("#173028")       # step consumed correctly, on the accepted path
_TRAP_COLOR = QColor("#2B1518")       # step where the input actually fell into q_trap
_ACCEPT_COLOR = QColor("#0F2A20")     # the final accepting cell, if the run was accepted

class AutomataPage(QWidget):
    """Automata Theory & Tables Explorer.
    
    Displays the formal 5-tuple, the delta transition matrix, the regular
    expression breakdown, and the minimization partition summary — all
    loaded dynamically from SimulationService.get_metadata(). When a
    SimulationResult from the last run is available, every section is
    additionally annotated to explain *that specific input*: which cells
    of δ it walked through, where (if anywhere) it fell into the dead
    state, and why the RE did or didn't match. Only reachable from the
    Simulator Page once a run has finished.
    """

    def __init__(self, simulation_service, on_check_another, on_back_to_simulator, on_view_tests=None, parent=None) -> None:
        super().__init__(parent)
        self._service = simulation_service
        self._on_check_another = on_check_another
        self._on_back_to_simulator = on_back_to_simulator
        self._on_view_tests = on_view_tests
        self._result = None

        back_btn = QPushButton("←  Back")
        back_btn.setObjectName("GhostButton")
        back_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        back_btn.clicked.connect(self._on_check_another_clicked)

        title = QLabel("Automata Theory & Tables")
        title.setObjectName("PageTitle")

        self._subtitle = QLabel("Formal definition of the minimized DFA used by the simulator.")
        self._subtitle.setObjectName("PageSubtitle")

        header_text = QVBoxLayout()
        header_text.setSpacing(2)
        header_text.addWidget(title)
        header_text.addWidget(self._subtitle)

        self._copy_markdown_btn = QPushButton("📋  Copy Markdown Trace")
        self._copy_markdown_btn.setObjectName("SecondaryButton")
        self._copy_markdown_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._copy_markdown_btn.clicked.connect(self._copy_markdown_report)

        header_row = QHBoxLayout()
        header_row.addWidget(back_btn)
        header_row.addSpacing(16)
        header_row.addLayout(header_text)
        header_row.addStretch()
        header_row.addWidget(self._copy_markdown_btn)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        content_layout.setSpacing(18)
        content_layout.setContentsMargins(2, 2, 2, 2)

        self._trace_card = self._make_section("Current Input Analysis")
        self._tuple_card = self._make_section("Formal Definition  —  M = (Q, Σ, δ, q₀, F)")
        self._re_card = self._make_section("Regular Expression")
        self._matrix_card = self._make_section("δ — Transition Matrix (minimized DFA)")
        self._min_card = self._make_section("Minimization Summary")

        content_layout.addWidget(self._trace_card)
        content_layout.addWidget(self._tuple_card)
        content_layout.addWidget(self._re_card)
        content_layout.addWidget(self._matrix_card)
        content_layout.addWidget(self._min_card)

        scroll.setWidget(content)

        check_another_btn = QPushButton("Check Another ID")
        check_another_btn.setObjectName("PrimaryButton")
        check_another_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        check_another_btn.clicked.connect(self._on_check_another_clicked)

        back_to_sim_btn = QPushButton("Back to Simulator  →")
        back_to_sim_btn.setObjectName("SecondaryButton")
        back_to_sim_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        back_to_sim_btn.clicked.connect(self._on_back_to_simulator_clicked)

        bottom_row = QHBoxLayout()
        bottom_row.addWidget(check_another_btn)
        if self._on_view_tests:
            test_suite_btn = QPushButton("📋  Test Suite")
            test_suite_btn.setObjectName("SecondaryButton")
            test_suite_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            test_suite_btn.clicked.connect(self._on_view_tests)
            bottom_row.addWidget(test_suite_btn)
        bottom_row.addStretch()
        bottom_row.addWidget(back_to_sim_btn)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 20, 28, 20)
        layout.setSpacing(14)
        layout.addLayout(header_row)
        layout.addWidget(scroll, 1)
        layout.addLayout(bottom_row)

    def _make_section(self, heading: str) -> QFrame:
        card = QFrame()
        card.setObjectName("AutomataCard")
        card.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

        label = QLabel(heading)
        label.setObjectName("AutomataCardHeading")

        body_container = QVBoxLayout()
        body_container.setObjectName("AutomataCardBody")

        layout = QVBoxLayout(card)
        layout.setSpacing(10)
        layout.addWidget(label)
        layout.addLayout(body_container)

        card.setProperty("body_layout", body_container)
        return card

    def _clear_body(self, card: QFrame) -> QVBoxLayout:
        body: QVBoxLayout = card.property("body_layout")
        while body.count():
            item = body.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        return body

    def refresh(self, result=None) -> None:
        """Reload every section from the current automata metadata, annotated
        against `result` (the SimulationResult of the last run, if any)."""
        self._result = result
        metadata = self._service.get_metadata()

        if result is not None:
            self._subtitle.setText(f'Explaining the run for "{result.input_string}".')
        else:
            self._subtitle.setText("Formal definition of the minimized DFA used by the simulator.")

        self._populate_trace(result)
        self._populate_tuple(metadata)
        self._populate_regex(metadata, result)
        self._populate_matrix(metadata, result)
        self._populate_minimization(metadata, result)

    # Current Input Analysis
    def _populate_trace(self, result) -> None:
        body = self._clear_body(self._trace_card)

        if result is None:
            placeholder = QLabel("Run a simulation first, then come back here to see exactly "
                                  "which states and transitions that input walked through.")
            placeholder.setObjectName("PageSubtitle")
            placeholder.setWordWrap(True)
            body.addWidget(placeholder)
            return

        verdict = QLabel("✔ ACCEPTED" if result.accepted else "✘ REJECTED")
        verdict.setObjectName("StatusLabel")
        verdict.setProperty("state", "accepted" if result.accepted else "rejected")
        verdict.setAlignment(Qt.AlignmentFlag.AlignCenter)
        verdict.style().unpolish(verdict)
        verdict.style().polish(verdict)
        body.addWidget(verdict)

        explanation = QLabel(f'Input "{result.input_string}"  —  {result.explanation}')
        explanation.setObjectName("PageSubtitle")
        explanation.setWordWrap(True)
        body.addWidget(explanation)

        if not result.trace:
            return

        table = QTableWidget(len(result.trace), 5)
        table.setObjectName("MatrixTable")
        table.setHorizontalHeaderLabels(["Step", "Symbol", "From", "To", "Status"])
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        table.verticalHeader().setVisible(False)
        table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        table.setMinimumHeight(min(300, 40 + 30 * len(result.trace)))

        for row, step in enumerate(result.trace):
            values = [str(step.step), step.symbol, step.from_state, step.to_state,
                      "OK" if step.is_valid else "TRAP"]
            for col, value in enumerate(values):
                item = QTableWidgetItem(value)
                if not step.is_valid:
                    item.setBackground(_TRAP_COLOR)
                elif result.accepted and row == len(result.trace) - 1:
                    item.setBackground(_ACCEPT_COLOR)
                table.setItem(row, col, item)

        body.addWidget(table)

    # Formal Definition 
    def _populate_tuple(self, metadata) -> None:
        body = self._clear_body(self._tuple_card)
        lines = [
            f"Q  = {{ {', '.join(metadata.states)} }}",
            f"Σ  = {{ {', '.join(metadata.alphabet)} }}",
            "δ  : Q × Σ → Q   (see the transition matrix below)",
            f"q₀ = {metadata.start_state}",
            f"F  = {{ {', '.join(metadata.accepting_states)} }}",
        ]
        for line in lines:
            label = QLabel(line)
            label.setObjectName("MonoLine")
            label.setWordWrap(True)
            body.addWidget(label)

    # Regular Expression
    def _populate_regex(self, metadata, result) -> None:
        body = self._clear_body(self._re_card)
        label = QLabel(metadata.re_pattern)
        label.setObjectName("MonoLine")
        label.setWordWrap(True)
        body.addWidget(label)

        breakdown = QLabel(
            "EMP  — fixed literal prefix\n"
            "-    — required separator\n"
            "[0-9]{4}  — 4-digit year segment (YYYY)\n"
            "-    — required separator\n"
            "[0-9]{4}  — 4-digit employee number segment (NNNN)"
        )
        breakdown.setObjectName("PageSubtitle")
        breakdown.setWordWrap(True)
        body.addWidget(breakdown)

        if result is None:
            return

        verdict_text = (
            f'"{result.input_string}" matches this pattern — every segment lined up correctly.'
            if result.accepted else
            f'"{result.input_string}" does NOT match this pattern. {result.explanation}'
        )
        verdict = QLabel(verdict_text)
        verdict.setObjectName("MonoLine")
        verdict.setWordWrap(True)
        body.addWidget(verdict)

    # Transition Matrix 
    def _populate_matrix(self, metadata, result) -> None:
        body = self._clear_body(self._matrix_card)
        symbols = metadata.alphabet
        states = metadata.states
        table = QTableWidget(len(states), len(symbols) + 1)
        table.setObjectName("MatrixTable")
        table.setHorizontalHeaderLabels(["State"] + symbols)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        table.verticalHeader().setVisible(False)
        table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        table.setMinimumHeight(min(420, 40 + 34 * len(states)))

        for row, state in enumerate(states):
            label = state
            if state == metadata.start_state:
                label += "  (start)"
            if state in metadata.accepting_states:
                label += "  (final)"
            table.setItem(row, 0, QTableWidgetItem(label))

            row_map = metadata.transition_table.get(state, {})
            for col, symbol in enumerate(symbols, start=1):
                table.setItem(row, col, QTableWidgetItem(row_map.get(symbol, "—")))

        if result is not None:
            self._highlight_path(table, states, symbols, result)

        body.addWidget(table)

        if result is not None:
            note = QLabel(self._matrix_note(result, symbols))
            note.setObjectName("PageSubtitle")
            note.setWordWrap(True)
            body.addWidget(note)

    def _highlight_path(self, table: QTableWidget, states: list[str], symbols: list[str], result) -> None:
        for i, step in enumerate(result.trace):
            if step.from_state not in states:
                continue
            row = states.index(step.from_state)

            if step.symbol not in symbols:
                # Invalid symbol -> no matching column exists; mark the row's
                # state name so it's still clear WHERE the run was standing.
                item = table.item(row, 0)
                if item:
                    item.setBackground(_TRAP_COLOR)
                continue

            col = symbols.index(step.symbol) + 1
            item = table.item(row, col)
            if not item:
                continue
            if not step.is_valid:
                item.setBackground(_TRAP_COLOR)
            elif result.accepted and i == len(result.trace) - 1:
                item.setBackground(_ACCEPT_COLOR)
            else:
                item.setBackground(_USED_COLOR)

    def _matrix_note(self, result, symbols: list[str]) -> str:
        if result.accepted:
            return "Highlighted cells trace the accepted path from q₀ to a final state."
        if result.status.name == "REJECTED_INVALID_SYMBOL" and result.error_position is not None:
            bad_symbol = result.input_string[result.error_position]
            return (f'Highlighted cell shows where the run stood right before hitting \'{bad_symbol}\' '
                    f"— that symbol isn't in Σ = {{ {', '.join(symbols)} }}, so no column exists for it "
                    "and δ is undefined there.")
        return "The red cell is the exact (state, symbol) pair where δ sends the run into q_trap."

    # Minimization Summary
    def _populate_minimization(self, metadata, result) -> None:
        body = self._clear_body(self._min_card)
        summary = metadata.minimization_summary
        line1 = QLabel(
            f"Unminimized states: {summary.get('unminimized_states', '—')}    "
            f"→    Minimized states: {summary.get('minimized_states', '—')}"
        )
        line1.setObjectName("MonoLine")
        body.addWidget(line1)

        notes = QLabel(summary.get("merged_groups", ""))
        notes.setObjectName("PageSubtitle")
        notes.setWordWrap(True)
        body.addWidget(notes)

        if result is None:
            return

        visited = sorted({step.from_state for step in result.trace} | {result.final_state or ""})
        visited = [s for s in visited if s]
        relevance = QLabel(
            f'For "{result.input_string}", the run only ever touched: {{ {", ".join(visited)} }} — '
            "every one of those is already a distinct state in the minimized machine, so no further "
            "merging applies to this particular path."
        )
        relevance.setObjectName("MonoLine")
        relevance.setWordWrap(True)
        body.addWidget(relevance)

    def _on_check_another_clicked(self) -> None:
        self._on_check_another()

    def _on_back_to_simulator_clicked(self) -> None:
        self._on_back_to_simulator()

    def _copy_markdown_report(self) -> None:
        from PySide6.QtWidgets import QApplication
        from PySide6.QtCore import QTimer

        metadata = self._service.get_metadata()
        lines = [
            "# Automata Theory Validation Report",
            "**Course:** CCAUTOMA — 1st AY 2026",
            "**Automaton:** Minimized DFA ($M = (Q, \\Sigma, \\delta, q_0, F)$)",
            f"**States ($Q$):** {len(metadata.states)} states (`{', '.join(metadata.states)}`)",
            f"**Alphabet ($\\Sigma$):** {len(metadata.alphabet)} symbols (`{', '.join(metadata.alphabet)}`)",
            f"**Start State ($q_0$):** `{metadata.start_state}`",
            f"**Accepting States ($F$):** `{', '.join(metadata.accepting_states)}`",
            f"**Regular Expression:** `{metadata.re_pattern}`",
            "",
        ]

        if self._result is not None:
            res = self._result
            verdict = "ACCEPTED" if res.accepted else "REJECTED"
            lines.extend([
                f"## Evaluation for Input: `{res.input_string}`",
                f"- **Verdict:** **{verdict}**",
                f"- **Status Code:** `{res.status.name}`",
                f"- **Final State:** `{res.final_state or 'None'}`",
                f"- **Symbols Processed:** {res.processed_symbols} / {res.total_symbols}",
                f"- **Explanation:** {res.explanation}",
                "",
                "### Symbol-by-Symbol Transition Trace",
                "| Step | Symbol | From State | To State | Valid? | Step Explanation |",
                "| :---: | :---: | :---: | :---: | :---: | :--- |",
            ])
            for step in res.trace:
                valid_str = "Yes" if step.is_valid else "No (Trap)"
                lines.append(
                    f"| {step.step} | `{step.symbol}` | `{step.from_state}` | `{step.to_state}` | {valid_str} | {step.explanation} |"
                )
        else:
            lines.append("*(No individual input has been simulated yet. Run an ID to view the full trace.)*")

        markdown_text = "\n".join(lines)
        clipboard = QApplication.clipboard()
        if clipboard:
            clipboard.setText(markdown_text)

        self._copy_markdown_btn.setText("✔  Copied to Clipboard!")
        QTimer.singleShot(2500, lambda: self._copy_markdown_btn.setText("📋  Copy Markdown Trace"))