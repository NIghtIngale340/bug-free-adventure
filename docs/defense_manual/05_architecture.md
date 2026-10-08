# 05 — Software Architecture

[← 04 Verification](04_verification.md) · [Index](README.md) · Next: [06 Validation Flows →](06_validation_flows.md)

Slide: **8 — Software Architecture**  
Presenter: **Chester Lauzon — Programmer / Automata Optimizer**

---

## 1. Overview: Clean Architectural Layering

In many student projects, business logic and UI code are tangled together: a button click event directly iterates through characters and sets label colors. 

In our project, we enforced a strict **Three-Tier Architecture**:

```text
┌────────────────────────────────────────────────────────┐
│                   PRESENTATION LAYER                   │
│             PySide6 GUI (app/gui/pages/)               │
│        SimulatePage  ·  TheoryPage  ·  TestsPage       │
│      (Pure display; contains ZERO automata logic)      │
└───────────────────────────┬────────────────────────────┘
                            │ Calls services
                            ▼
┌────────────────────────────────────────────────────────┐
│                     SERVICE LAYER                      │
│                  (app/services/)                       │
│        SimulationService  ·  ValidationService         │
│  (Session state, playback control, result packaging)   │
└───────────────────────────┬────────────────────────────┘
                            │ Drives execution
                            ▼
┌────────────────────────────────────────────────────────┐
│                     AUTOMATA CORE                      │
│                     (app/core/)                        │
│   regex.py · nfa.py · dfa.py · minimizer.py            │
│   pipeline.py · simulator.py · equivalence.py          │
│       (Pure algorithms; completely independent of Qt)   │
└───────────────────────────┬────────────────────────────┘
                            │ References rules
                            ▼
┌────────────────────────────────────────────────────────┐
│                      DATA LAYER                        │
│                     (app/data/)                        │
│         id_rules.py (ID_REGEX, Σ) · test_cases.py      │
└────────────────────────────────────────────────────────┘
```

---

## 2. Layer-by-Layer Responsibilities

### Tier 1: Presentation Layer (`app/gui/`)
- **Technology:** PySide6 (Qt for Python).
- **Files:**
  - `pages/simulate_page.py`: Interactive simulation canvas, symbol tape, transition stepper, verdict banner.
  - `pages/theory_page.py`: 8 tabs displaying generated tables, state diagrams, and theoretical derivations.
  - `pages/tests_page.py`: Test suite execution table, batch input area, pass/fail indicators.
  - `widgets/`: Reusable display widgets (`tape_widget.py`, `verdict_banner.py`, `diagram_widget.py`).
- **Core Rule:** **The GUI never makes validation decisions.** It never inspects characters or decides whether a string is valid. It takes a `SimulationResult` object from the service layer and simply paints it on screen.

### Tier 2: Service Layer (`app/services/`)
- **Files:**
  - `simulation_service.py`: Coordinates interactive simulation sessions. Manages play/pause timers, stepping forward/backward, and remembers which model is active (minimal DFA, subset DFA, or ε-NFA).
  - `validation_service.py`: Provides fast, one-shot validation methods for individual strings and batch lists.
- **Responsibility:** Acts as a bridge. It converts raw user inputs into simulation requests, calls the Automata Core, and packages the outputs into UI-friendly data structures.

### Tier 3: Automata Core (`app/core/`)
This is the intellectual heart of the project. It has **zero dependencies on Qt or GUI code**.
- `regex.py`: Defines the AST nodes (`ConcatNode`, `LiteralNode`, `DigitClassNode`, `RepeatNode`) and builds the formal representation.
- `nfa.py`: Implements Thompson's Construction, $\varepsilon$-closure, $\text{move}(S, a)$, and Rabin–Scott Subset Construction.
- `dfa.py`: Defines the formal `DFA` data class with an explicit, total transition function.
- `minimizer.py`: Implements Moore's Partition Refinement algorithm and records every intermediate round ($P_0 \dots P_{13}$).
- `equivalence.py`: Implements the Product Automaton BFS equivalence prover and counterexample generator.
- `pipeline.py`: Compiles the complete pipeline (`build_pipeline()`) once and caches the resulting machines.
- `simulator.py`: Implements the execution engine (`Run` class).
- `language.py`: Implements Layer 1 alphabet filtering and Unicode validation.

### Tier 4: Data Layer (`app/data/`)
- `id_rules.py`: Contains the single source of truth: `ID_REGEX = "EMP-D⁴-D⁴"`. Every other property (alphabet $\Sigma$, valid length 13) is derived programmatically from this rule.
- `test_cases.py`: Stores the 28 predefined test cases (10 valid, 18 invalid) with human descriptions.

---

## 3. The Core Principle: "The GUI Contains Zero Automata Logic"

If a panel member asks: *"Where is the code that actually decides whether an ID is accepted?"*, Chester Lauzon should explain:

> "The decision logic lives entirely inside `app/core/simulator.py` and `app/core/dfa.py`. The GUI does not contain a single `if-else` statement about ID validity."

### Why This Architectural Separation Matters:
1. **Academic Integrity:** The software faithfully models theoretical automata. The GUI is merely an observer watching the mathematical machine step through states.
2. **Headless Testability:** Because the automata core has zero Qt imports, our unit and integration tests run in milliseconds in pure Python. The entire test suite can run in CI/CD without an X11/Wayland display server.
3. **Zero UI-Engine Divergence:** If you change how the diagram looks, you can never accidentally break how IDs are validated.
4. **Portability:** If we wanted to deploy this project as a Web App (FastAPI + React) or a Command-Line Interface (CLI), we could reuse `app/core/` and `app/services/` with 100% code reuse.

---

## 4. The Single Source of Truth: `app.core.simulator.Run`

A common defect in student GUI simulators is having **two different engines**:
- A fast backend function used for automated testing (`def is_valid(s): return ...`)
- A separate visual stepping function inside the UI (`def step_forward(self): ...`)

When a project does this, the fast validator and the visual simulator can quietly diverge!

### Our Solution: Unified `Run` Engine
In our project, `app.core.simulator.Run` is the **single engine** that powers everything:
```text
                       app.core.simulator.Run
                                 │
         ┌───────────────────────┼───────────────────────┐
         ▼                       ▼                       ▼
   Fast Batch Run          Step-by-Step UI          Pytest Suite
   (One-shot loop)       (Interactive Canvas)    (Differential Tests)
```

- When you press **"Run All"**, `simulate()` iterates `Run.step()` until completion.
- When you press **"Step Forward"**, the GUI calls `Run.step()` exactly once.
- When you press **"Step Backward"**, `Run` steps backward using its historical trace.
- When automated tests run 20,000 strings, they invoke the exact same `Run` class.

This guarantees that **the GUI animation and the validation verdict can never disagree**.

---

## 5. The Three Validation Layers

Every string entered by a user passes through three distinct layers in order:

```text
User Input String
       │
       ▼
[ Layer 1: Alphabet Pre-Filter ] ──(Invalid symbol ∉ Σ)──► REJECTED_INVALID_SYMBOL
       │                                                    (Reports symbol & position)
       ▼ (All symbols ∈ Σ)
[ Layer 2: Automaton Traversal ] ──(No transition / trap)─► REJECTED_NO_TRANSITION
       │                                                    (Reports state & position)
       ▼ (String consumed)
[ Layer 3: Presentation Packaging]
       ├── If current_state ∈ F  ───────────────► ACCEPTED
       └── If current_state ∉ F  ───────────────► REJECTED_NON_FINAL_STATE
```

1. **Layer 1 — Alphabet Pre-Filter (`app/core/language.py`):**
   - Scans the raw string to ensure every character belongs to $\Sigma$.
   - If an invalid character is found (e.g. `'A'` in `EMP-2026-12A4`), it rejects immediately with `REJECTED_INVALID_SYMBOL`, identifies the symbol `'A'`, and reports index 11.
   - The DFA never sees characters outside $\Sigma$, preserving the formal domain $\delta: Q \times \Sigma \to Q$.

2. **Layer 2 — Automaton Traversal (`app/core/simulator.py`):**
   - Steps through the minimal DFA symbol by symbol.
   - If a symbol in $\Sigma$ is unexpected at that position (e.g. `'2'` instead of `'-'` at state $q_3$), $\delta(q_3, '2') = q_{\text{trap}}$.
   - It transitions into $q_{\text{trap}}$ and terminates with `REJECTED_NO_TRANSITION`.

3. **Layer 3 — Presentation Packaging (`app/services/`):**
   - Evaluates whether the final state is in $F = \{q_{13}\}$.
   - Formats the trace, highlights the active state, and produces the final user-facing verdict banner.
