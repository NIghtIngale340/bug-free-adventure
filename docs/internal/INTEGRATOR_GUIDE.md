> **Historical planning document.** It describes the original three-person plan (including a mock backend and a hand-written DFA). The implementation has moved on — see `docs/architecture.md` and the code.

# DEVELOPER PLAYBOOK — INTEGRATOR & TECHNICAL LEAD
## Repository Governance, Git Merging, Integration QA, and Defense Guide

**Developer:** You (The Integrator / Technical Lead)  
**Role:** Integration Lead / Repository Governor / System Coordinator  
**Target Platform:** Python 3.12+ | PySide6 | pytest | Git/GitHub  
**Primary Directory Ownership:** `app/main.py`, `app/data/test_cases.py`, `tests/integration/`, `docs/`, `requirements.txt`, `pyproject.toml`, `.gitignore`

---

## 1. Role Overview & Boundaries

You are the **architectural anchor, Git administrator, quality assurance lead, and defense coordinator**. Your job is to ensure Ken's automata core and Chester's PySide6 GUI integrate seamlessly without friction.

### What You Own:
* Repository configuration: `requirements.txt`, `pyproject.toml`, `.gitignore`, and virtual environment guidance.
* Shared contract enforcement: Defining and freezing `app/core/models.py`.
* Unblocking the team: Maintaining `app/services/mock_service.py` so Chester can build the GUI in parallel with Ken.
* Master test data: Curating 25+ accepted and rejected Employee IDs in `app/data/test_cases.py`.
* Application bootstrap: Wiring real services into the GUI inside `app/main.py`.
* End-to-end testing: Authoring automated pipeline tests in `tests/integration/test_e2e_pipeline.py`.
* Git review & merging: Reviewing PRs from Ken and Chester, resolving merge conflicts, maintaining `develop` and `main`.
* Master academic report: Consolidating theory chapters from Ken and UI diagrams from Chester into the final report.
* Defense coordination: Orchestrating the 4-minute live demonstration and question preparation for September 29 / October 2.

### What You MUST NOT Do:
* **DO NOT write everyone's code.** Ken owns the backend algorithms; Chester owns the UI widgets. You facilitate, review, and test.
* **DO NOT merge unreviewed or failing PRs into `develop`.**
* **DO NOT silently alter the agreed formal language or API contracts.**

---

## 2. Your Integration Tasks Roadmap

| Task ID | Task Name | Target File(s) | Dependencies | Complexity |
| :--- | :--- | :--- | :--- | :---: |
| **INT-001** | Repo Environment, Tooling & Config | `requirements.txt`<br>`pyproject.toml`<br>`.gitignore` | None | Low |
| **INT-002** | Shared Data Contracts & Mock Service | `app/core/models.py`<br>`app/services/mock_service.py` | INT-001 | Medium |
| **INT-003** | Master Test Cases Dataset (25+ IDs) | `app/data/test_cases.py` | INT-002 | Low |
| **INT-004** | Application Entry Point & DI Wiring | `app/main.py` | BE-006, FE-001 | Medium |
| **INT-005** | End-to-End Integration Test Suite | `tests/integration/test_e2e_pipeline.py` | INT-004 | Medium |
| **INT-006** | PR Reviews, Merging & Git Health | Repository-wide | Continuous | Ongoing |
| **INT-007** | Master Academic Report Consolidation | `docs/*` | Theory/UI docs ready | Medium |
| **INT-008** | Defense Rehearsal & Release Tagging | `v1.0.0-defense` | All tests passing | Medium |

---

## 3. Git & GitHub Governance Workflow

```
main (Protected: Release Builds Only)
  │
  └── develop (Integration Staging: All PRs Merge Here)
       │
       ├── feat/be-...  (Ken's feature branches)
       ├── feat/fe-...  (Chester's feature branches)
       └── feat/int-... (Your integration branches)
```

### 3.1 Daily Git Setup & Review Protocol
As the Integrator, use this workflow when reviewing and merging teammate PRs:

#### Step 1: Fetch and Check Out Teammate's PR Branch Locally
```bash
git fetch origin
git checkout feat/be-005-simulator-core
```

#### Step 2: Run Verification Checks (Gatekeeper Routine)
Run the linter and the automated test suite locally:
```bash
# 1. Run linter
ruff check .

# 2. Run all existing tests
pytest -v
```
*If tests fail or linter errors appear:* Reject the PR or request changes on GitHub with explicit failure logs.

#### Step 3: Fast-Forward or Squash-Merge into `develop`
```bash
git checkout develop
git pull origin develop
git merge --no-ff feat/be-005-simulator-core -m "merge(be): integrate BE-005 simulator core"
git push origin develop
```

---

## 4. Conflict Resolution Protocol

If Ken and Chester's branches create a merge conflict:
1. **Never resolve conflicts blind inside the GitHub web editor.**
2. Check out the conflicted feature branch locally:
   ```bash
   git checkout feat/fe-004-simulator-page
   git fetch origin
   git rebase origin/develop
   ```
3. Open conflicting files. Ensure that backend logic and GUI code have not contaminated the same module.
4. Run tests post-resolution:
   ```bash
   pytest
   ```
5. Force push the resolved branch with lease:
   ```bash
   git push origin feat/fe-004-simulator-page --force-with-lease
   ```
6. Complete the merge into `develop`.

---

## 5. Master Test Cases Dataset (`app/data/test_cases.py`)

You will maintain the authoritative list of test cases used across integration tests and Page 4 of the GUI:

```python
"""
MASTER TEST DATASET: 25+ Categorized Test Cases
Owner: Integrator
Used by: tests/integration/test_e2e_pipeline.py and app/gui/pages/test_cases_page.py
"""

from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class TestCase:
    id: str
    input_str: str
    expected_accepted: bool
    category: str
    expected_reason: str


MASTER_TEST_SUITE: List[TestCase] = [
    # --- VALID TEST CASES (10 minimum) ---
    TestCase("TC-VAL-01", "EMP-2026-0001", True, "Valid Standard", "Standard valid ID"),
    TestCase("TC-VAL-02", "EMP-2026-0042", True, "Valid Standard", "Standard valid ID"),
    TestCase("TC-VAL-03", "EMP-2026-9999", True, "Valid Standard", "Max sequence number"),
    TestCase("TC-VAL-04", "EMP-2000-0000", True, "Valid Boundary", "Boundary year 2000"),
    TestCase("TC-VAL-05", "EMP-2099-1234", True, "Valid Boundary", "Boundary year 2099"),
    TestCase("TC-VAL-06", "EMP-1999-5555", True, "Valid Standard", "Historical year 1999"),
    TestCase("TC-VAL-07", "EMP-2024-8765", True, "Valid Standard", "Recent year 2024"),
    TestCase("TC-VAL-08", "EMP-2025-0101", True, "Valid Standard", "Valid sequence"),
    TestCase("TC-VAL-09", "EMP-2027-3333", True, "Valid Future", "Future year 2027"),
    TestCase("TC-VAL-10", "EMP-2030-7777", True, "Valid Future", "Future year 2030"),

    # --- INVALID PREFIX ---
    TestCase("TC-INV-01", "AXP-2026-0001", False, "Invalid Prefix", "Prefix is not 'EMP'"),
    TestCase("TC-INV-02", "emp-2026-0001", False, "Invalid Prefix", "Prefix must be uppercase"),
    TestCase("TC-INV-03", "EM-2026-0001", False, "Invalid Prefix", "Prefix too short"),
    TestCase("TC-INV-04", "EMPP-2026-0001", False, "Invalid Prefix", "Prefix too long"),

    # --- INVALID SEPARATORS ---
    TestCase("TC-INV-05", "EMP2026-0001", False, "Missing Separator", "Missing first hyphen"),
    TestCase("TC-INV-06", "EMP-20260001", False, "Missing Separator", "Missing second hyphen"),
    TestCase("TC-INV-07", "EMP_2026_0001", False, "Wrong Separator", "Underscore instead of hyphen"),
    TestCase("TC-INV-08", "EMP--2026-0001", False, "Extra Separator", "Consecutive hyphens"),

    # --- INVALID YEAR ---
    TestCase("TC-INV-09", "EMP-26-0001", False, "Invalid Year", "Year too short (2 digits)"),
    TestCase("TC-INV-10", "EMP-20261-0001", False, "Invalid Year", "Year too long (5 digits)"),
    TestCase("TC-INV-11", "EMP-202A-0001", False, "Invalid Year", "Non-numeric character in year"),

    # --- INVALID SEQUENCE NUMBER ---
    TestCase("TC-INV-12", "EMP-2026-1", False, "Invalid Sequence", "Sequence too short"),
    TestCase("TC-INV-13", "EMP-2026-00001", False, "Invalid Sequence", "Sequence too long"),
    TestCase("TC-INV-14", "EMP-2026-12B4", False, "Invalid Sequence", "Letter inside numeric sequence"),

    # --- SPECIAL & EMPTY STRINGS ---
    TestCase("TC-INV-15", "", False, "Empty Input", "Empty input string"),
    TestCase("TC-INV-16", "EMP-2026-0001 ", False, "Trailing Whitespace", "Trailing space character"),
    TestCase("TC-INV-17", " EMP-2026-0001", False, "Leading Whitespace", "Leading space character"),
    TestCase("TC-INV-18", "EMP-2026-00!1", False, "Invalid Symbol", "Symbol '!' outside alphabet Sigma"),
]
```

---

## 6. End-to-End Integration Test Suite (`tests/integration/test_e2e_pipeline.py`)

You will author this test to verify the complete integrated system:

```python
"""
END-TO-END INTEGRATION TEST SUITE
Verifies contract adherence and batch execution of the Master Test Cases.
"""

import pytest
from app.services.validation_service import ValidationService
from app.data.test_cases import MASTER_TEST_SUITE


@pytest.fixture
def validator():
    return ValidationService()


@pytest.mark.parametrize("tc", MASTER_TEST_SUITE, ids=lambda tc: tc.id)
def test_master_suite_compliance(validator, tc):
    result = validator.validate(tc.input_str)
    assert result.accepted == tc.expected_accepted, (
        f"Test {tc.id} failed for '{tc.input_str}'. "
        f"Expected accepted={tc.expected_accepted}, got {result.accepted}. "
        f"Explanation: {result.explanation}"
    )
```

---

## 7. Application Bootstrap & Service Injection (`app/main.py`)

When Ken's core and Chester's GUI are merged, you connect them together in `app/main.py`:

```python
"""
APPLICATION ENTRY POINT & DEPENDENCY INJECTION
Owner: Integrator
"""

import sys
from PySide6.QtWidgets import QApplication
from app.services.validation_service import ValidationService
from app.services.simulation_service import SimulationService
from app.gui.main_window import MainWindow


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Employee ID Validator — Automata Theory")

    # Instantiate real backend services
    val_service = ValidationService()
    sim_service = SimulationService()

    # Inject into main GUI window
    window = MainWindow(validation_service=val_service, simulation_service=sim_service)
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
```

---

## 8. 48-Hour Pre-Defense Audit Checklist

Before stepping into the oral examination on **September 29 / October 2**:

- [ ] **Clean Virtual Environment Verification:**
  ```bash
  python -m venv .clean_venv
  source .clean_venv/bin/activate
  pip install -r requirements.txt
  python -m app.main
  ```
- [ ] **100% Test Pass:** `pytest -v` runs with zero failures and zero warnings across `tests/core/`, `tests/services/`, `tests/gui/`, and `tests/integration/`.
- [ ] **Lint Cleanliness:** `ruff check .` returns clean.
- [ ] **All 25+ Test Cases Pass:** Page 4 of the GUI runs the test suite with 100% green checkmarks.
- [ ] **Offline Readiness:** App launches and runs completely offline with zero network connectivity.
- [ ] **Release Tag:** Git release tagged: `git tag -a v1.0.0-defense -m "Release for Academic Defense"`.
- [ ] **Defense Rehearsal:** Timed 4-minute demo rehearsed twice with Ken and Chester.
- [ ] **Backup Hardware:** Working copy of the repository configured on at least two team laptops.
