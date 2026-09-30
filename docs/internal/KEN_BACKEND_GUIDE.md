> **Historical planning document.** It describes the original three-person plan (including a mock backend and a hand-written DFA). The implementation has moved on — see `docs/architecture.md` and the code.

# DEVELOPER PLAYBOOK — KEN (BACKEND & AUTOMATA CORE LEAD)
## Automata Theory Core, Simulation Engine, and Service Layer Guide

**Developer:** Ken  
**Role:** Backend / Automata Core Lead  
**Target Platform:** Python 3.12+ | pytest  
**Primary Directory Ownership:** `app/core/`, `app/services/`, `tests/core/`, `tests/services/`, `app/data/id_rules.py`

---

## 1. Role Overview & Boundaries

Ken is the **mathematical and algorithmic owner** of the Employee ID Validator. You are responsible for transforming formal automata concepts into high-performance, testable Python code that runs behind the GUI.

### What You Own:
* The formal language configuration ($\Sigma$, grammar, string length constraints).
* Automata mathematical models: NFA, DFA, and the Minimized DFA.
* Algorithmic implementations: Subset Construction ($NFA \rightarrow DFA$) and Hopcroft Partition Refinement (DFA Minimization).
* The deterministic simulation engine that steps through the Minimized DFA symbol-by-symbol and records state transitions.
* The application service layer (`ValidationService`, `SimulationService`) that wraps core logic for Chester's GUI.
* Comprehensive unit tests in `tests/core/` and `tests/services/`.

### What You MUST NOT Do:
* **NEVER import PySide6, PyQt, or any UI modules.** Backend code must remain 100% headless and executable from the terminal.
* **NEVER modify files inside `app/gui/` or `assets/`.**
* **NEVER unilaterally change the formal language format (`EMP-YYYY-NNNN`).** Any adjustment requires 3-way consensus.
* **NEVER return raw unformatted tuples or debug print statements.** Always return the frozen dataclasses defined in `app/core/models.py`.

---

## 2. Your Task Roadmap

| Task ID | Task Name | Target File(s) | Dependencies | Complexity |
| :--- | :--- | :--- | :--- | :---: |
| **BE-001** | Formal Language & Alphabet Validator | `app/core/language.py`<br>`app/data/id_rules.py` | None | Low |
| **BE-002** | Automata Data Models & Shared Types | `app/core/models.py` | BE-001 | Medium |
| **BE-003** | NFA Model & Subset Construction | `app/core/nfa.py`<br>`app/core/dfa.py` | BE-002 | High |
| **BE-004** | Hopcroft DFA Minimization Engine | `app/core/minimizer.py` | BE-003 | High |
| **BE-005** | Minimized DFA Simulator & Trace Engine | `app/core/simulator.py` | BE-002, BE-004 | Medium |
| **BE-006** | Service Facades (`Validation` & `Simulation`) | `app/services/validation_service.py`<br>`app/services/simulation_service.py` | BE-005 | Medium |
| **BE-007** | Core & Service pytest Unit Test Suite | `tests/core/*`<br>`tests/services/*` | BE-001 to BE-006 | Medium |

---

## 3. Task Specifications & Acceptance Criteria

### Task BE-001: Formal Language & Alphabet Validator
* **Files:** `app/core/language.py`, `app/data/id_rules.py`
* **Responsibilities:**
  - Define $\Sigma = \{\text{'E'}, \text{'M'}, \text{'P'}, \text{'-'}, \text{'0'}-\text{'9'}\}$.
  - Provide `is_symbol_in_alphabet(char: str) -> bool`.
  - Provide `validate_symbols(input_str: str) -> Tuple[bool, List[Tuple[int, str]]]` returning any illegal characters with their indices.
* **Criteria:** Tests pass in `tests/core/test_language.py`.

### Task BE-002: Automata Data Models
* **Files:** `app/core/models.py`
* **Responsibilities:**
  - Implement shared dataclasses matching [docs/SHARED_ARCHITECTURE_AND_CONTRACTS.md](SHARED_ARCHITECTURE_AND_CONTRACTS.md): `TransitionStep`, `SimulationResult`, `AutomataMetadata`, and `SimulationStatus`.
  - Provide internal primitives: `DFAState`, `DFATransition`.
* **Criteria:** Co-reviewed with Integrator before Chester imports types.

### Task BE-003: NFA & Subset Construction
* **Files:** `app/core/nfa.py`, `app/core/dfa.py`
* **Responsibilities:**
  - Formally represent the 13-symbol recognition NFA: $M = (Q, \Sigma, \delta, q_0, F)$.
  - Implement subset construction to derive deterministic DFA state groups.
  - Store transitions as `Dict[str, Dict[str, str]]`.
* **Criteria:** DFA transitions deterministically process `EMP-[0-9]{4}-[0-9]{4}`.

### Task BE-004: DFA Minimization Engine
* **Files:** `app/core/minimizer.py`
* **Responsibilities:**
  - Prune unreachable states from the DFA.
  - Divide states into initial partition $P_0 = \{F, Q \setminus F\}$.
  - Iteratively refine partitions until $k$-equivalence stability is reached.
  - Record merged state history (e.g. $\{q_a, q_b\} \rightarrow q_{new}$) for academic defense reporting.
  - Produce canonical Minimized DFA with an explicit dead/trap state (`"q_trap"`).
* **Criteria:** Equivalence tests verify Minimized DFA accepts the exact same language as unminimized DFA.

### Task BE-005: Minimized DFA Simulator & Trace Engine
* **Files:** `app/core/simulator.py`
* **Responsibilities:**
  - Traverse the Minimized DFA symbol-by-symbol for any input string.
  - If a symbol causes an invalid transition or is outside $\Sigma$, transition immediately to `"q_trap"` or mark failure.
  - Record an immutable `TransitionStep` for each character consumed.
  - Return complete `SimulationResult`.
* **Criteria:** Zero unhandled crashes on empty strings, non-alphabet symbols, or long strings.

### Task BE-006: Application Service Layer
* **Files:** `app/services/validation_service.py`, `app/services/simulation_service.py`
* **Responsibilities:**
  - Implement `ValidationService.validate(input_string: str) -> SimulationResult` (one-shot validation for Page 1).
  - Implement `SimulationService`:
    - `create_session(input_string: str) -> str`: allocates stateful session.
    - `step(session_id: str) -> Optional[TransitionStep]`: advances 1 character; returns `None` at string end.
    - `run_all(session_id: str) -> SimulationResult`: finishes remaining steps.
    - `reset(session_id: str) -> None`: resets to $q_0$.
    - `get_metadata() -> AutomataMetadata`: exports table data for Page 3.
* **Criteria:** Replaces `app/services/mock_service.py` with zero interface changes.

### Task BE-007: Core Unit Test Suite
* **Files:** `tests/core/`, `tests/services/`
* **Responsibilities:**
  - Test valid IDs: `EMP-2026-0001`, `EMP-1999-9999`, `EMP-2099-0042` (`accepted=True`).
  - Test invalid IDs: bad prefix (`AXP-...`), missing hyphens (`EMP2026-0001`), bad length (`EMP-26-0001`), bad symbols (`EMP-2026-12A4`), empty string (`""`).
  - Assert trace step counts match input lengths for complete runs.
* **Criteria:** `pytest tests/core tests/services` passes 100% with zero warnings.

---

## 4. What You Must Provide to Chester (The Frontend Contract)

Chester is building the GUI against the interfaces in `models.py`. Your implementation **must return data matching these exact shapes**:

### 1. One-Shot Validation (`ValidationService.validate`)
```python
# What Chester calls:
result = validation_service.validate("EMP-2026-0042")

# What you must return (SimulationResult):
SimulationResult(
    input_string="EMP-2026-0042",
    accepted=True,
    status=SimulationStatus.ACCEPTED,
    final_state="q13",
    trace=[
        TransitionStep(step=1, symbol="E", from_state="q0", to_state="q1", is_valid=True, explanation="Prefix match 'E'"),
        ...
        TransitionStep(step=13, symbol="2", from_state="q12", to_state="q13", is_valid=True, explanation="Final digit accepted")
    ],
    error_message=None,
    error_position=None,
    processed_symbols=13,
    total_symbols=13,
    explanation="Input recognized as valid Employee ID."
)
```

### 2. Step-by-Step Simulation (`SimulationService.step`)
```python
# Chester creates a session and calls step() repeatedly:
session_id = sim_service.create_session("EMP-2026-0042")
step_1 = sim_service.step(session_id)

# What you must return (TransitionStep):
TransitionStep(
    step=1,
    symbol="E",
    from_state="q0",
    to_state="q1",
    is_valid=True,
    explanation="Valid prefix symbol 'E'"
)
```

---

## 5. Ken's Git Workflow

1. Always branch from the latest `develop`:
   ```bash
   git checkout develop
   git pull origin develop
   git checkout -b feat/be-005-simulator-core
   ```
2. Commit with Conventional Commits:
   ```bash
   git commit -m "feat(core): implement step-by-step trace generation in simulator"
   ```
3. Test locally before opening a PR:
   ```bash
   pytest tests/core tests/services
   ruff check app/core app/services
   ```
4. Push and open a PR targeting `develop`. Request review from the Integrator.

---

## 6. Backend Completion Checklist (Definition of Done)

Before declaring your work complete for integration:

- [ ] All code resides strictly in `app/core/`, `app/services/`, and `app/data/id_rules.py`.
- [ ] No `import PySide6` or GUI dependencies anywhere in your code.
- [ ] Language validator rejects any character outside $\Sigma$.
- [ ] Hopcroft minimizer produces a verified Minimized DFA.
- [ ] Simulator produces complete, immutable `SimulationResult` and `TransitionStep` objects.
- [ ] `ValidationService` and `SimulationService` match `models.py` contracts 100%.
- [ ] 100% of unit tests pass: `pytest tests/core tests/services`.
- [ ] Documentation files drafted in `docs/`:
  - [ ] `docs/formal_language.md`
  - [ ] `docs/regex.md`
  - [ ] `docs/nfa.md`
  - [ ] `docs/dfa.md`
  - [ ] `docs/minimization.md`
- [ ] Ready to answer oral defense questions on subset construction and minimization partitioning.
