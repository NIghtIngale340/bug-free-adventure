> **Historical planning document.** It describes the original three-person plan (including a mock backend and a hand-written DFA). The implementation has moved on — see `docs/architecture.md` and the code.

# DEVELOPER PLAYBOOK — CHESTER (FRONTEND & GUI LEAD)
## PySide6 Desktop Application, Interactive Views, and UI State Guide

**Developer:** Chester  
**Role:** Frontend / PySide6 GUI Lead  
**Target Platform:** Python 3.12+ | PySide6 (Qt for Python)  
**Primary Directory Ownership:** `app/gui/`, `assets/`, `tests/gui/`

---

## 1. Role Overview & Boundaries

Chester is the **visual architect and user experience lead** of the Employee ID Validator. You are responsible for transforming raw automata state transitions into a polished, responsive desktop application that makes automata theory easily explainable to the academic examination panel.

### What You Own:
* The main PySide6 application window and sidebar navigation router (`app/gui/main_window.py`).
* All 4 required application views:
  1. **Validator Dashboard:** Fast Employee ID input, instant validation, large status card, state indicators.
  2. **Step-by-Step DFA Simulator:** Interactive playback (`Next Step`, `Run All`, `Reset`), live character ribbon tracking, and dynamic transition table.
  3. **Automata Theory & Tables Explorer:** Displays the formal 5-tuple, NFA/DFA tables, and minimization partition summary.
  4. **Predefined Test Suite Runner:** Displays 25+ test cases with one-click batch execution and pass/fail indicators.
* Reusable UI widgets: `ResultCard`, `TransitionTable`, `StateView`.
* Application visual theme and styling (`app/gui/styles/theme.qss`).
* Frontend interaction tests (`tests/gui/`).

### What You MUST NOT Do:
* **NEVER write automata algorithms or string slicing inside GUI buttons.** The UI must never check `"if input_str.startswith('EMP')"` or run independent regex matching.
* **NEVER duplicate validation logic.** All validation decisions must come strictly from `ValidationService` and `SimulationService`.
* **NEVER modify files inside `app/core/` or backend test files.**
* **NEVER introduce external heavy web frameworks, databases, or non-Qt UI dependencies.**

---

## 2. Your Task Roadmap

| Task ID | Task Name | Target File(s) | Dependencies | Complexity |
| :--- | :--- | :--- | :--- | :---: |
| **FE-001** | PySide6 Shell, Navigation & Theme | `app/gui/main_window.py`<br>`app/gui/styles/theme.qss` | Environment set | Medium |
| **FE-002** | Reusable UI Component Library | `app/gui/widgets/*` | FE-001 | Medium |
| **FE-003** | Page 1 — Validator Dashboard | `app/gui/pages/validator_page.py` | FE-002, Mock Service | Medium |
| **FE-004** | Page 2 — Step-by-Step DFA Simulator | `app/gui/pages/simulator_page.py` | FE-002, Mock Service | High |
| **FE-005** | Page 3 — Automata Theory Explorer | `app/gui/pages/automata_page.py` | FE-001, Mock Service | Medium |
| **FE-006** | Page 4 — Predefined Test Suite Runner | `app/gui/pages/test_cases_page.py` | FE-002, Test Dataset | Medium |
| **FE-007** | PySide6 Headless Interaction Tests | `tests/gui/*` | FE-001 to FE-006 | Medium |

---

## 3. How to Develop Without Waiting for Ken (Mock Backend)

To allow you to build the entire GUI immediately in parallel, the Integrator has defined a drop-in `MockAutomataService` in `app/services/mock_service.py` that satisfies the frozen service interface:

```python
"""
DROP-IN MOCK SERVICE FOR FRONTEND DEVELOPMENT
Import this into your pages during Phase 2.
When Ken's core is ready, the Integrator will swap this with real services.
"""

from app.core.models import (
    SimulationResult,
    SimulationStatus,
    TransitionStep,
    AutomataMetadata,
)


class MockAutomataService:
    def validate(self, input_string: str) -> SimulationResult:
        if not input_string:
            return SimulationResult(
                input_string="",
                accepted=False,
                status=SimulationStatus.REJECTED_EMPTY_INPUT,
                final_state=None,
                trace=[],
                error_message="Input string cannot be empty.",
                error_position=None,
                processed_symbols=0,
                total_symbols=0,
                explanation="Please enter an Employee ID.",
            )

        is_valid = (input_string == "EMP-2026-0042")
        trace = [
            TransitionStep(1, "E", "q0", "q1", True, "Prefix 'E'"),
            TransitionStep(2, "M", "q1", "q2", True, "Prefix 'M'"),
            TransitionStep(3, "P", "q2", "q3", True, "Prefix 'P'"),
            TransitionStep(4, "-", "q3", "q4", True, "Separator '-'"),
        ]
        return SimulationResult(
            input_string=input_string,
            accepted=is_valid,
            status=SimulationStatus.ACCEPTED if is_valid else SimulationStatus.REJECTED_NON_FINAL_STATE,
            final_state="q13" if is_valid else "q_trap",
            trace=trace,
            error_message=None if is_valid else "Rejected: Sample mock failure.",
            error_position=None if is_valid else 4,
            processed_symbols=len(input_string),
            total_symbols=len(input_string),
            explanation="Valid ID recognized." if is_valid else "ID rejected by DFA.",
        )

    def create_session(self, input_string: str) -> str:
        return "mock_session_1"

    def step(self, session_id: str) -> TransitionStep | None:
        # Returns one TransitionStep or None when finished
        return TransitionStep(1, "E", "q0", "q1", True, "Step 1: Prefix 'E'")

    def run_all(self, session_id: str) -> SimulationResult:
        return self.validate("EMP-2026-0042")

    def reset(self, session_id: str) -> None:
        pass

    def get_metadata(self) -> AutomataMetadata:
        return AutomataMetadata(
            states=["q0", "q1", "q2", "q3", "q4", "q13", "q_trap"],
            alphabet=["E", "M", "P", "-", "0", "1", "2", "3", "4", "5", "6", "7", "8", "9"],
            start_state="q0",
            accepting_states=["q13"],
            transition_table={"q0": {"E": "q1"}},
            re_pattern=r"^EMP-[0-9]{4}-[0-9]{4}$",
            minimization_summary={"unminimized_states": 18, "minimized_states": 14},
        )
```

---

## 4. UI Page Architecture & Widget Details

### 4.1 Page 1: Validator Dashboard (`validator_page.py`)
* **Input Box:** `QLineEdit` with placeholder `"e.g. EMP-2026-0042"`.
* **Action Buttons:** `[Validate]` (primary action, bound to Return key) and `[Clear]`.
* **Result Banner (`ResultCard` widget):**
  - Displays **ACCEPTED** in bold emerald green (`#10B981`) or **REJECTED** in crimson red (`#EF4444`).
  - Readout fields: `Final State` (e.g. `q13`), `Symbols Processed` (e.g. `13 / 13`), `Explanation`.
* **Defensive UX:** If the user clicks `[Validate]` with an empty input, display a gentle warning banner without throwing an exception.

### 4.2 Page 2: Step-by-Step DFA Simulator (`simulator_page.py`)
This is the **flagship defense page**. The examination panel will evaluate how clearly this view illustrates DFA state traversal.
* **Input Bar:** Allows loading any ID string into the stepping session.
* **Control Bar:**
  - `[Start / Load]`: Calls `SimulationService.create_session(input_str)`.
  - `[Next Step]`: Calls `SimulationService.step(session_id)`. Appends one row to the table, moves the ribbon cursor forward, updates `Current State` and `Next State` badges.
  - `[Run All / Fast-Forward]`: Automatically iterates until `step()` returns `None`.
  - `[Reset]`: Calls `SimulationService.reset(session_id)`, clears the table, and resets the cursor to index 0.
* **Visual Ribbon:** Displays the input string with a dynamic highlight box pointing to the active symbol.
* **Transition Table (`TransitionTable` widget):** Columns: `[Step, Symbol, From State, To State, Status]`.

### 4.3 Page 3: Automata Theory Explorer (`automata_page.py`)
* Displays formal course definitions loaded dynamically from `SimulationService.get_metadata()`:
  - 5-tuple: $M = (Q, \Sigma, \delta, q_0, F)$.
  - Regular Expression breakdown.
  - Transition Matrix ($\delta$).
  - Minimization partition history summary.

### 4.4 Page 4: Predefined Test Suite Runner (`test_cases_page.py`)
* Loads 25+ test cases from `app/data/test_cases.py`.
* Button: `[Run All Test Cases]`.
* Displays table with columns: `Test ID`, `Input String`, `Category`, `Expected`, `Actual`, `Status (PASS/FAIL)`.
* Clicking any row automatically loads that string into the **Step-by-Step Simulator** for immediate visual debugging.

---

## 5. Chester's Git Workflow

1. Always branch from latest `develop`:
   ```bash
   git checkout develop
   git pull origin develop
   git checkout -b feat/fe-004-simulator-page
   ```
2. Commit with Conventional Commits:
   ```bash
   git commit -m "feat(gui): implement step-by-step playback controls and ribbon cursor"
   ```
3. Test locally before opening a PR:
   ```bash
   python -m pytest tests/gui
   ruff check app/gui
   ```
4. Push and open a PR targeting `develop`. Request review from the Integrator.

---

## 6. Frontend Completion Checklist (Definition of Done)

Before declaring your work complete for integration:

- [ ] All 4 application pages are implemented and accessible via the sidebar navigation.
- [ ] Application window renders cleanly at standard resolutions (1080p, 720p) with zero widget overlapping.
- [ ] No automata algorithms, regex parsing, or string logic are hardcoded inside UI widgets.
- [ ] Pages interact with backend exclusively through `ValidationService` and `SimulationService`.
- [ ] Empty inputs, rapid button clicks, and malformed strings cause zero application crashes.
- [ ] Step-by-step simulator buttons enable/disable properly at boundary conditions (e.g. `Next Step` disabled when string finishes).
- [ ] Application stylesheet (`theme.qss`) provides clean, high-contrast, academic styling.
- [ ] PySide6 tests pass: `pytest tests/gui`.
- [ ] Screenshots captured for report and saved to `assets/screenshots/`.
- [ ] UI documentation written in `docs/ui_design.md`.
- [ ] Ready to demonstrate live step-by-step simulation during oral defense rehearsal.
