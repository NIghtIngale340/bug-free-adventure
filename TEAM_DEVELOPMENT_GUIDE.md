# TEAM DEVELOPMENT GUIDE & MASTER HUB
## 3-Person Developer Playbook: Employee ID Validator (CCAUTOMA 2026)

**Project:** Employee ID Validator – Organization-Defined ID Structure  
**Defense Dates:** September 29, 2026 & October 2, 2026  
**Primary Stack:** Python 3.12+ | PySide6 | pytest  
**Repository State:** Architecture frozen; folder structure initialized.

---

## 1. Quick Navigation: Read Your Role Guide First

To keep everyone focused on what they need to deliver without information overload, **each team member has their own dedicated playbook**:

| Team Member | Role | Assigned Playbook | Primary Focus Areas |
| :--- | :--- | :--- | :--- |
| **Ken** | **Backend / Automata Core Lead** | [docs/KEN_BACKEND_GUIDE.md](file:///home/nightingale/Desktop/Automata_WTF/docs/KEN_BACKEND_GUIDE.md) | Formal Language, NFA/DFA, Hopcroft Minimizer, Simulator, Services, Core pytest |
| **Chester** | **Frontend / GUI Lead** | [docs/CHESTER_FRONTEND_GUIDE.md](file:///home/nightingale/Desktop/Automata_WTF/docs/CHESTER_FRONTEND_GUIDE.md) | PySide6 Shell, 4 GUI Pages, Step Simulator View, Custom Widgets, QSS Theme |
| **You (Integrator)** | **Integration & Technical Lead** | [docs/INTEGRATOR_GUIDE.md](file:///home/nightingale/Desktop/Automata_WTF/docs/INTEGRATOR_GUIDE.md) | Git Branching, PR Reviews, Merging, E2E Testing, Main Wiring, Defense Coordination |
| **All Members** | **Shared Technical Contracts** | [docs/SHARED_ARCHITECTURE_AND_CONTRACTS.md](file:///home/nightingale/Desktop/Automata_WTF/docs/SHARED_ARCHITECTURE_AND_CONTRACTS.md) | Formal Language ($L, \Sigma$), Data Models (`SimulationResult`), 10 Team Rules |
| **All Members** | **Automata Theory Baseline** | [docs/AUTOMATA_THEORY_BASELINE.md](file:///home/nightingale/Desktop/Automata_WTF/docs/AUTOMATA_THEORY_BASELINE.md) | Canonical state names ($q_0 \dots q_{13}, q_{\text{trap}}$), transition matrix, minimization proof |
| **All Members** | **Local Environment Setup** | [docs/SETUP_AND_ENVIRONMENT.md](file:///home/nightingale/Desktop/Automata_WTF/docs/SETUP_AND_ENVIRONMENT.md) | 3-step setup for Linux/macOS/Windows, PySide6 XCB troubleshooting, test commands |
| **All Members** | **Git Workflow Cheatsheet** | [docs/GIT_CHEATSHEET.md](file:///home/nightingale/Desktop/Automata_WTF/docs/GIT_CHEATSHEET.md) | Morning routine, safe branch creation, PR guidelines, conflict resolution, panic buttons |
| **All Members** | **Oral Defense Playbook** | [docs/DEFENSE_SCRIPT_AND_QA.md](file:///home/nightingale/Desktop/Automata_WTF/docs/DEFENSE_SCRIPT_AND_QA.md) | 4-minute demo choreography (word-for-word script) & 12 panel trap questions with answers |

---

## 2. Project Architecture & Directory Ownership

The folder structure is officially initialized. Developers must work strictly within their assigned boundaries:

```
employee-id-validator/
│
├── README.md                           <- Project overview & quickstart
├── TEAM_DEVELOPMENT_GUIDE.md           <- [YOU ARE HERE] Master navigation hub
├── PROJECT_SPEC_EMPLOYEE_ID_VALIDATOR.md <- Course specification reference
│
├── docs/                               <- [INTEGRATOR / TEAM] Documentation & Playbooks
│   ├── SHARED_ARCHITECTURE_AND_CONTRACTS.md  <- Shared contracts & 10 rules
│   ├── AUTOMATA_THEORY_BASELINE.md           <- Single source of truth for DFA states & delta
│   ├── KEN_BACKEND_GUIDE.md                  <- Ken's backend task playbook
│   ├── CHESTER_FRONTEND_GUIDE.md             <- Chester's frontend task playbook
│   ├── INTEGRATOR_GUIDE.md                   <- Integrator's git & QA playbook
│   ├── SETUP_AND_ENVIRONMENT.md              <- OS setup & PySide6 troubleshooting
│   ├── GIT_CHEATSHEET.md                     <- Safe Git commands & conflict resolution
│   └── DEFENSE_SCRIPT_AND_QA.md              <- 4-min live demo script & panel Q&A bank
│
├── app/
│   ├── main.py                         <- [INTEGRATOR] App entry point & DI wiring
│   ├── core/                           <- [KEN] Automata theory logic (models, dfa, minimizer, sim)
│   ├── services/                       <- [KEN / INTEGRATOR] Service facades & mock service
│   ├── gui/                            <- [CHESTER] PySide6 UI views, widgets, and styles
│   │   ├── pages/                      <- [CHESTER] Validator, Simulator, Automata, Test pages
│   │   ├── widgets/                    <- [CHESTER] Result card, transition table, state view
│   │   └── styles/                     <- [CHESTER] QSS theme stylesheet
│   └── data/                           <- [INTEGRATOR / KEN] ID rules & master 25+ test cases
│
├── tests/
│   ├── core/                           <- [KEN] Automata & language unit tests
│   ├── services/                       <- [KEN] Service layer tests
│   ├── gui/                            <- [CHESTER] Headless PySide6 interaction tests
│   └── integration/                    <- [INTEGRATOR] End-to-end master test suite
│
└── assets/                             <- [CHESTER / INTEGRATOR]
    ├── diagrams/                       <- State diagrams (NFA, DFA, Minimized DFA)
    └── screenshots/                    <- Application UI screenshots for academic report
```

---

## 3. High-Level Non-Blocking Workflow

To prevent team members from blocking one another:

1. **Phase 1 — Contract Freeze (Days 1–2):** The shared data models (`SimulationResult`, `TransitionStep`) and mock service are frozen.
2. **Phase 2 — Parallel Execution (Days 2–4):**
   - **Ken** builds the Automata Core, Minimizer, Simulator, and Unit Tests in `app/core/` and `app/services/` using `pytest`.
   - **Chester** builds the PySide6 application shell, all 4 pages, and widgets in `app/gui/` using `MockAutomataService`.
   - **Integrator** maintains Git repository health, prepares master test cases (`app/data/test_cases.py`), and drafts E2E test harnesses.
3. **Phase 3 — Service Swap & Merge (Days 4–5):** Ken's backend is merged into `develop`. Chester swaps the mock for real services.
4. **Phase 4 — System Integration & QA (Days 5–6):** Chester's GUI is merged. Integrator runs automated E2E tests against all 25+ test cases.
5. **Phase 5 — Report & Defense Rehearsal (Days 7–8):** Master academic report assembled; timed 4-minute demo rehearsed. Release tagged for defense on **September 29 / October 2**.

---

## 4. The 10 Immutable Team Rules

1. **The Minimized DFA is the Sole Source of Truth:** Never use regex or string heuristics to determine acceptance.
2. **The GUI Contains Zero Automata Algorithms:** Transitions happen strictly inside Ken's backend core.
3. **Backend Code Never Imports PySide6:** Ken's code must remain 100% headless and testable from the terminal.
4. **Shared Contracts Are Frozen Before Implementation:** All team members build to the agreed `models.py` contracts.
5. **No Silent Breaking Changes:** Modifying any method in `models.py` requires unanimous 3-person consent.
6. **Every Feature Requires Automated Tests:** No PR is merged without passing unit tests in `pytest`.
7. **Every Pull Request Explains What Changed:** PR descriptions must cite task IDs, files touched, and test commands.
8. **Integrator Governs Merges; Teammates Own Their Code:** The Integrator reviews and merges, but does not rewrite teammates' logic.
9. **Formal Language Audits Are Mandatory If Rules Change:** Any change to `EMP-YYYY-NNNN` requires an immediate 3-way sync.
10. **All Three Members Must Be Able to Defend the System:** "Own one module, review two modules, understand all modules."

---

## 5. Daily Git Hygiene Command Cheatsheet

Run this every morning before writing new code:

```bash
# 1. Update your local develop branch
git checkout develop
git pull origin develop

# 2. Switch to your active feature branch
git checkout feat/<your-task-id>

# 3. Rebase on top of latest develop
git rebase develop
```

*For role-specific step-by-step instructions, see your playbook in the `docs/` directory.*
