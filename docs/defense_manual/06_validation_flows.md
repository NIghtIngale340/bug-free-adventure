# 06 — Validation Flows & Under-the-Hood Walkthrough

[← 05 Architecture](05_architecture.md) · [Index](README.md) · Next: [07 Presentation Flow →](07_presentation_flow.md)

Slides: **10 — Demo: An Accepted ID**, **11 — Two Rejection Modes**  
Presenters: **James Dotosme** (Accepted flow) · **Mark Anub** & **Chester Lauzon** (Two rejection modes)

---

## 1. Overview: How an Input is Processed

When a user types an Employee ID into CCAUTOMA, the system does not guess or use heuristic string splitting. Every input follows an explicit mathematical pathway through our validation layers.

Below are step-by-step traces for all four canonical test categories.

---

## 2. Walkthrough 1: Valid Input (`EMP-2026-0042`)

### 1. User Input
The user enters `EMP-2026-0042` and clicks **Run All** (or steps through with **Step Forward**).

### 2. Layer 1: Alphabet Pre-Filter
- `app/core/language.py::validate_symbols` scans the 13 characters.
- Every character (`E`, `M`, `P`, `-`, `2`, `0`, `2`, `6`, `-`, `0`, `0`, `4`, `2`) belongs to:
  $$\Sigma = \{'E', 'M', 'P', '-', '0', \dots, '9'\}$$
- **Layer 1 verdict:** PASS. Passes the string to Layer 2.

### 3. Layer 2: Automaton Traversal
The minimal DFA begins at initial state **$q_0$**. The simulation engine (`Run`) steps forward symbol by symbol:

```text
Step  Pos  Symbol  From  To    Transition Rule                Status
───────────────────────────────────────────────────────────────────────
 1     0    'E'    q0    q1    δ(q0, 'E') = q1                OK
 2     1    'M'    q1    q2    δ(q1, 'M') = q2                OK
 3     2    'P'    q2    q3    δ(q2, 'P') = q3                OK
 4     3    '-'    q3    q4    δ(q3, '-') = q4                OK
 5     4    '2'    q4    q5    δ(q4, '2') = q5                OK (Year d1)
 6     5    '0'    q5    q6    δ(q5, '0') = q6                OK (Year d2)
 7     6    '2'    q6    q7    δ(q6, '2') = q7                OK (Year d3)
 8     7    '6'    q7    q8    δ(q7, '6') = q8                OK (Year d4)
 9     8    '-'    q8    q9    δ(q8, '-') = q9                OK
 10    9    '0'    q9    q10   δ(q9, '0') = q10               OK (Seq d1)
 11   10    '0'    q10   q11   δ(q10, '0') = q11              OK (Seq d2)
 12   11    '4'    q11   q12   δ(q11, '4') = q12              OK (Seq d3)
 13   12    '2'    q12   q13   δ(q12, '2') = q13              OK (Seq d4)
```

### 4. Layer 3: Presentation Packaging
- Input string is completely consumed (13 / 13 symbols).
- Final state reached is **$q_{13}$**.
- Check accepting set: $q_{13} \in F = \{q_{13}\}$ $\implies$ **ACCEPTED**.
- Status: `SimulationStatus.ACCEPTED`.

### 5. GUI Rendering
- **Verdict Banner:** Displays vibrant emerald green **ACCEPTED** badge.
- **Interactive Tape:** Highlights index 12 in green; regex segment indicators show all four blocks matched (Prefix `EMP`, Separator `-`, Year `2026`, Sequence `0042`).
- **Canvas Diagram:** State $q_{13}$ glows green with a double circle; the entire sequential path from $q_0$ to $q_{13}$ is highlighted in green.

---

## 3. Walkthrough 2: Structural Rejection (`EMP2026-0001`)

### 1. User Input
The user enters `EMP2026-0001` (missing the first hyphen separator).

### 2. Layer 1: Alphabet Pre-Filter
- Checks symbols: `'E'`, `'M'`, `'P'`, `'2'`, `'0'`, `'2'`, `'6'`, `'-'`, `'0'`, `'0'`, `'0'`, `'1'`.
- Notice: **Every single symbol is in $\Sigma$!** Digit `'2'` is a valid alphabet symbol.
- **Layer 1 verdict:** PASS.

### 3. Layer 2: Automaton Traversal
The minimal DFA runs normally through the prefix:
1. $q_0 \xrightarrow{E} q_1$
2. $q_1 \xrightarrow{M} q_2$
3. $q_2 \xrightarrow{P} q_3$

At state **$q_3$**, the automaton has recognized `"EMP"` and requires the separator `'-'`.
However, the next input symbol is **`'2'`** at position 3:
- In the DFA transition table: $\delta(q_3, '-') = q_4$.
- For all other symbols in $\Sigma$: $\delta(q_3, '2') = \mathbf{q_{\text{trap}}}$.
- The machine enters dead state **$q_{\text{trap}}$**.
- **Early Stop Optimization:** Once inside $q_{\text{trap}}$, no string can ever reach an accepting state ($d(q_{\text{trap}}, F) = \infty$). The simulation halts immediately to avoid wasting cycles.

### 4. Layer 3: Presentation Packaging
- Status: `SimulationStatus.REJECTED_NO_TRANSITION`.
- Error location: Position 3 (0-indexed).
- Offending symbol: `'2'`.
- Expected symbol: `'-'`.
- Reached state: $q_{\text{trap}}$.

### 5. GUI Rendering
- **Verdict Banner:** Displays bold crimson **REJECTED** banner:  
  *"Structural Error: Unexpected symbol '2' at position 3. Expected '-' from state q3."*
- **Interactive Tape:** Highlights position 3 in red.
- **Canvas Diagram:** Shows a **dashed red transition line** leaving $q_3$ and pointing directly into $q_{\text{trap}}$. The trap state is highlighted in warning red.

---

## 4. Walkthrough 3: Alphabet Rejection (`EMP-2026-12A4`)

### 1. User Input
The user enters `EMP-2026-12A4` (contains the letter `'A'`, which is not a digit).

### 2. Layer 1: Alphabet Pre-Filter
- `app/core/language.py::validate_symbols` inspects each character:
  - Pos 0–10: `'E', 'M', 'P', '-', '2', '0', '2', '6', '-', '1', '2'` $\in \Sigma$.
  - Pos 11: **`'A' \notin \Sigma$`**.
- **Layer 1 verdict:** **FAIL**. Immediately halts!

### 3. Layer 2: Automaton Traversal
- **The DFA NEVER RUNS.**
- **Why?** In formal automata theory, the transition function $\delta$ is only defined for symbols in $\Sigma$. Character `'A'` is not in $\Sigma$, so $\delta(q, 'A')$ is mathematically undefined. Running the DFA on `'A'` would violate formal definition.

### 4. Layer 3: Presentation Packaging
- Status: `SimulationStatus.REJECTED_INVALID_SYMBOL`.
- Error location: Position 11 (0-indexed).
- Offending symbol: `'A'`.
- Error message: `"Symbol 'A' at position 11 is not in the alphabet Σ = {E, M, P, -, 0–9}"`.

### 5. GUI Rendering
- **Verdict Banner:** Bright red banner stating that an invalid alphabet symbol was rejected at position 11.
- **Interactive Tape:** Flags character `'A'` with a red badge.
- **Canvas Diagram:** Displays an alert; zero states are traversed on the graph.

---

## 5. Walkthrough 4: Whitespace Errors

### 1. User Input
User accidentally pastes an ID with a leading space: `' EMP-2026-0001'` or a trailing space: `'EMP-2026-0001 '`.

### 2. The Trap Question: "Does the GUI auto-trim whitespace?"
> **CRITICAL RULE:** **The GUI NEVER trims or modifies user input.**

Why? In security and identity management, silent input trimming masks data corruption. If an automated API sends an ID with leading spaces, silently trimming it hides the bug.

### 3. Processing
- Space `' '` is checked against $\Sigma$.
- ASCII space ($0x20$) is **not in $\Sigma$**.
- Layer 1 rejects the string immediately at Position 0 (for leading space) or Position 13 (for trailing space).
- Status: `REJECTED_INVALID_SYMBOL`.
- GUI displays: `"Invalid symbol ' ' (space) at position 0"`.

---

## 6. What Actually Happens Inside the System? (Chronological Lifecycle)

Here is the exact lifecycle of the application from the moment the command is entered in the terminal to the rendering of the final result:

```text
1. Terminal Execution
   └─ $ python -m app.main
         │
2. Initialization & Pipeline Build (app/core/pipeline.py)
   ├─ Reads ID_REGEX = "EMP-D⁴-D⁴"
   ├─ regex.py: Parses string into Regex AST
   ├─ nfa.py: Walks AST with Thompson's Construction ──► Generates 26-state ε-NFA
   ├─ nfa.py: Executes Rabin-Scott Subset Construction ─► Generates 15-state DFA (with D_trap)
   ├─ minimizer.py: Runs Moore Partition Refinement ───► Proves 15 states minimal (q0…q13, q_trap)
   ├─ equivalence.py: Runs Product BFS ────────────────► Proves DFA_subset ≡ DFA_minimal (15 pairs, 0 errors)
   └─ Resulting pipeline objects are cached in memory (singleton pattern)
         │
3. GUI Launch (app/gui/main_window.py)
   ├─ Initializes PySide6 QApplication
   ├─ Creates MainWindow with Navigation Sidebar (Simulate, Theory, Tests)
   ├─ SimulatePage queries SimulationService to load the minimal DFA
   └─ DiagramWidget pre-renders the 15-state graph layout
         │
4. User Interaction (Simulate Page)
   ├─ User enters string: "EMP-2026-0042"
   ├─ User clicks "Run All" or presses Enter
   └─ GUI calls SimulationService.run_full("EMP-2026-0042")
         │
5. Execution Engine (app/core/simulator.py::Run)
   ├─ Layer 1 Check: language.validate_symbols("EMP-2026-0042")
   │    └─ Verifies all characters ∈ Σ
   ├─ Layer 2 Execution:
   │    ├─ Run object initialized at state q0
   │    ├─ Iterates through characters 0..12
   │    ├─ For each symbol, looks up δ(current_state, symbol)
   │    ├─ Appends transition record to history trace
   │    └─ Ends at q13
   └─ Evaluates final acceptance: q13 ∈ F ──► ACCEPTED
         │
6. Result Hand-Off & UI Repaint
   ├─ SimulationService returns SimulationResult object to SimulatePage
   ├─ VerdictBanner updates text and style to green ACCEPTED
   ├─ TapeWidget updates cursor and segments
   ├─ DiagramWidget repaints canvas, illuminating visited states and the active final state
   └─ TransitionHistoryTable lists all 13 transitions with timestamps and symbols
```
