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
        self._tuple_card = self._make_section("Formal Definition  —  M_DFA = (Q, Σ, δ, q₀, F)")
        self._nfa_card = self._make_section("NFA & Subset Construction  —  M_NFA → M_DFA")
        self._re_card = self._make_section("Regular Expression")
        self._matrix_card = self._make_section("δ — Transition Matrix (minimized DFA)")
        self._min_card = self._make_section("Minimization Summary")

        content_layout.addWidget(self._trace_card)
        content_layout.addWidget(self._tuple_card)
        content_layout.addWidget(self._nfa_card)
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
            self._subtitle.setText("Formal definition of the minimized DFA and canonical NFA used by the simulator.")

        self._populate_trace(result)
        self._populate_tuple(metadata)
        self._populate_nfa(metadata, result)
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

    # NFA & Subset Construction
    def _populate_nfa(self, metadata, result) -> None:
        body = self._clear_body(self._nfa_card)
        nfa_sum = metadata.nfa_summary or {}

        # 1. Formal 5-tuple
        nfa_states = nfa_sum.get("states", [])
        start = nfa_sum.get("start_state", "q0")
        accepting = nfa_sum.get("accepting_states", ["q13"])

        lines = [
            "M_NFA = (Q_NFA, Σ, δ_NFA, q₀, F_NFA)",
            f"Q_NFA  = {{ {', '.join(nfa_states)} }}  (14 linear states + ∅ dead state)",
            f"Σ      = {{ {', '.join(metadata.alphabet)} }}",
            f"q₀     = {start}",
            f"F_NFA  = {{ {', '.join(accepting)} }}",
        ]
        for line in lines:
            lbl = QLabel(line)
            lbl.setObjectName("MonoLine")
            lbl.setWordWrap(True)
            body.addWidget(lbl)

        # 2. Subset Construction mapping table
        subset_trace = nfa_sum.get("subset_trace", [])
        if subset_trace:
            table_heading = QLabel("Subset Construction Mapping (Rabin-Scott Algorithm):")
            table_heading.setObjectName("MonoLine")
            body.addWidget(table_heading)

            table = QTableWidget(len(subset_trace) + 1, 4)
            table.setObjectName("MatrixTable")
            table.setHorizontalHeaderLabels(["DFA State", "NFA Subset", "Automaton Meaning", "Valid Transition Class"])
            table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
            table.verticalHeader().setVisible(False)
            table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
            table.setMinimumHeight(min(320, 40 + 26 * (len(subset_trace) + 1)))

            meanings = {
                "D0": ("Initial state (ε-closure)", "'E' → {q1}"),
                "D1": ("Prefix 'E' consumed", "'M' → {q2}"),
                "D2": ("Prefix 'EM' consumed", "'P' → {q3}"),
                "D3": ("Prefix 'EMP' consumed", "'-' → {q4}"),
                "D4": ("Prefix 'EMP-' consumed", "0–9 → {q5}"),
                "D5": ("Year Digit 1 verified", "0–9 → {q6}"),
                "D6": ("Year Digit 2 verified", "0–9 → {q7}"),
                "D7": ("Year Digit 3 verified", "0–9 → {q8}"),
                "D8": ("Year YYYY complete", "'-' → {q9}"),
                "D9": ("Separator 'EMP-YYYY-' verified", "0–9 → {q10}"),
                "D10": ("Sequence Digit 1 verified", "0–9 → {q11}"),
                "D11": ("Sequence Digit 2 verified", "0–9 → {q12}"),
                "D12": ("Sequence Digit 3 verified", "0–9 → {q13}"),
                "D13": ("Sequence Digit 4 (NNNN) — ACCEPTING (F)", "Any Σ → ∅"),
            }

            for row, (dfa_name, subset_states) in enumerate(subset_trace):
                subset_str = "{" + ", ".join(subset_states) + "}"
                meaning, moves = meanings.get(dfa_name, ("Sequential state", "—"))
                s_name = subset_states[0] if subset_states else "?"
                table.setItem(row, 0, QTableWidgetItem(f"{dfa_name} ({s_name})"))
                table.setItem(row, 1, QTableWidgetItem(subset_str))
                table.setItem(row, 2, QTableWidgetItem(meaning))
                table.setItem(row, 3, QTableWidgetItem(moves))

            # Add dead state D_trap
            last_row = len(subset_trace)
            table.setItem(last_row, 0, QTableWidgetItem("D_trap (q_trap)"))
            table.setItem(last_row, 1, QTableWidgetItem("∅"))
            table.setItem(last_row, 2, QTableWidgetItem("Dead / Trap state (rejecting)"))
            table.setItem(last_row, 3, QTableWidgetItem("Any Σ → ∅"))

            # Highlight active path if run result is provided
            if result is not None and result.trace:
                visited = {step.from_state for step in result.trace} | {result.final_state or ""}
                for row, (dfa_name, subset_states) in enumerate(subset_trace):
                    sub_str = "{" + ", ".join(subset_states) + "}"
                    s_name = subset_states[0] if subset_states else ""
                    if sub_str in visited or s_name in visited:
                        is_final = result.accepted and (sub_str == result.final_state or s_name == result.final_state)
                        bg = _ACCEPT_COLOR if is_final else _USED_COLOR
                        for col in range(4):
                            it = table.item(row, col)
                            if it:
                                it.setBackground(bg)

            body.addWidget(table)

        note_text = nfa_sum.get("note", "")
        if note_text:
            note = QLabel(note_text)
            note.setObjectName("PageSubtitle")
            note.setWordWrap(True)
            body.addWidget(note)

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
        nfa_sum = metadata.nfa_summary or {}
        nfa_states = nfa_sum.get("states", [])

        lines = [
            "# Automata Theory Validation Report",
            "**Course:** CCAUTOMA — 1st AY 2026",
            "**Language:** $L = \\{ \\text{EMP-YYYY-NNNN} \\}$",
            "**Pipeline:** $\\text{Regular Expression} \\longrightarrow \\text{Canonical NFA} \\xrightarrow{\\text{Subset Construction}} \\text{DFA} \\xrightarrow{\\text{Hopcroft}} \\text{Minimized DFA}$",
            "",
            "## Formal Automata Specifications",
            "### 1. Canonical NFA ($M_{\\text{NFA}}$)",
            f"- **States ($Q_{{\\text{{NFA}}}}$):** {len(nfa_states)} linear states (`{', '.join(nfa_states)}`) + dead subset $\\emptyset$",
            f"- **Alphabet ($\\Sigma$):** {len(metadata.alphabet)} symbols (`{', '.join(metadata.alphabet)}`)",
            f"- **Start State ($q_0$):** `{nfa_sum.get('start_state', 'q0')}`",
            f"- **Accepting States ($F_{{\\text{{NFA}}}}$):** `{', '.join(nfa_sum.get('accepting_states', ['q13']))}`",
            "",
            "### 2. Minimized DFA ($M_{\\text{DFA}}$)",
            f"- **States ($Q$):** {len(metadata.states)} states (`{', '.join(metadata.states)}`)",
            f"- **Start State ($q_0$):** `{metadata.start_state}`",
            f"- **Accepting States ($F$):** `{', '.join(metadata.accepting_states)}`",
            f"- **Regular Expression:** `{metadata.re_pattern}`",
            "",
            "### 3. Rabin-Scott Subset Construction Mapping",
            "| DFA State | NFA State Subset | Description |",
            "| :---: | :---: | :--- |",
        ]
        for dfa_name, subset in nfa_sum.get("subset_trace", []):
            lines.append(f"| `{dfa_name}` | `{{{', '.join(subset)}}}` | Mapped 1-to-1 via $\\varepsilon$-closure |")
        lines.append("| `D_trap` | `∅` | Dead / Trap rejecting state |")
        lines.append("")

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