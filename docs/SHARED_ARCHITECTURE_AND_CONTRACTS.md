# SHARED ARCHITECTURE, CONTRACTS & TEAM RULES
## Employee ID Validator (Automata Theory Project — CCAUTOMA 2026)

**Audience:** All Team Members (Ken, Chester, Integrator)  
**Purpose:** Single technical source of truth for formal language, architecture, shared data contracts, and team governance.

---

## 1. Project Essence & Formal Language Definition

This project is an **educational Automata Theory software application**, not an HR database. Its primary objective is to prove that an organization-defined Employee ID format can be formally recognized using a **Minimized Deterministic Finite Automaton (DFA)** while rendering the symbol-by-symbol transition process in an interactive desktop GUI.

```
Organization ID Rules ──> Formal Language (Σ, L) ──> Regular Expression (RE)
         │
         ▼
      NFA ──(Subset Construction)──> DFA ──(Minimization)──> Minimized DFA
                                                                    │
                                                                    ▼
                                                            Python Simulator
                                                                    │
                                                                    ▼
                                                              PySide6 GUI
```

### 1.1 The Formal Language $L$
* **Format:** `EMP-YYYY-NNNN`
  - Fixed Prefix: `EMP` (3 uppercase characters)
  - Separator 1: `-` (Hyphen)
  - Year: `YYYY` (4 digits, `[0-9]{4}`)
  - Separator 2: `-` (Hyphen)
  - Sequential ID: `NNNN` (4 digits, `[0-9]{4}`)
* **Fixed Total Length:** Exactly 13 characters.
* **Alphabet $\Sigma$:**
  $$\Sigma = \{\text{'E'}, \text{'M'}, \text{'P'}, \text{'-'}, \text{'0'}, \text{'1'}, \text{'2'}, \text{'3'}, \text{'4'}, \text{'5'}, \text{'6'}, \text{'7'}, \text{'8'}, \text{'9'}\} \quad (|\Sigma| = 14)$$
* **Regular Expression:**
  $$\text{RE} = \text{EMP}-[0-9]{4}-[0-9]{4}$$

---

## 2. Decoupled 4-Layer Architecture

The system strictly decouples user interface code from automata mathematics.

```
┌────────────────────────────────────────────────────────┐
│                   1. GUI LAYER (Chester)               │
│         PySide6 Desktop Application & 4 Views          │
└───────────────────────────┬────────────────────────────┘
                            │ Calls public services
                            ▼
┌────────────────────────────────────────────────────────┐
│                2. SERVICE LAYER (Ken)                  │
│       ValidationService & SimulationService Facades    │
└───────────────────────────┬────────────────────────────┘
                            │ Drives automata
                            ▼
┌────────────────────────────────────────────────────────┐
│               3. AUTOMATA CORE (Ken)                   │
│   Language, NFA, DFA, Minimizer, Simulator Engine      │
└───────────────────────────┬────────────────────────────┘
                            │ Reads static rules
                            ▼
┌────────────────────────────────────────────────────────┐
│             4. DATA & CONFIG (Integrator / Ken)        │
│          Organization Rules & Master Test Dataset      │
└────────────────────────────────────────────────────────┘
```

---

## 3. Shared Data Contracts (`app/core/models.py`)

These dataclasses and enums represent the **immutable bridge** between Ken's backend and Chester's frontend. Neither party may alter these signatures without prior team consensus.

```python
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Any


class SimulationStatus(Enum):
    ACCEPTED = "ACCEPTED"
    REJECTED_INVALID_SYMBOL = "REJECTED_INVALID_SYMBOL"
    REJECTED_NON_FINAL_STATE = "REJECTED_NON_FINAL_STATE"
    REJECTED_NO_TRANSITION = "REJECTED_NO_TRANSITION"
    REJECTED_EMPTY_INPUT = "REJECTED_EMPTY_INPUT"


@dataclass(frozen=True)
class TransitionStep:
    """Represents a single symbol transition in the Minimized DFA."""
    step: int              # 1-indexed step number (1 to 13)
    symbol: str            # Current character evaluated ('E', '-', '2', etc.)
    from_state: str        # Source state (e.g. 'q0')
    to_state: str          # Destination state (e.g. 'q1' or 'q_trap')
    is_valid: bool         # True if valid transition; False if trapped
    explanation: str       # Human-readable step note for GUI tables


@dataclass(frozen=True)
class SimulationResult:
    """The complete outcome of an Employee ID validation."""
    input_string: str               # Raw input evaluated
    accepted: bool                  # True strictly if final_state in F
    status: SimulationStatus        # Detailed terminal status
    final_state: Optional[str]      # Final state reached (or None if empty)
    trace: List[TransitionStep]     # Chronological list of all transitions
    error_message: Optional[str]    # User-facing message if rejected
    error_position: Optional[int]   # 0-indexed index where error occurred
    processed_symbols: int          # Symbols processed before termination
    total_symbols: int              # Total length of input_string
    explanation: str                # Summary text for result card


@dataclass(frozen=True)
class AutomataMetadata:
    """Formal description of the Minimized DFA for theory display."""
    states: List[str]                            # Q
    alphabet: List[str]                          # Sigma
    start_state: str                             # q0
    accepting_states: List[str]                  # F
    transition_table: Dict[str, Dict[str, str]]  # delta: {state: {symbol: next_state}}
    re_pattern: str                              # RE string
    minimization_summary: Dict[str, Any]         # State count reduction stats
```

---

## 4. Public Service Signatures (`app/services/`)

Chester's GUI interacts exclusively with two service interfaces:

```python
from abc import ABC, abstractmethod
from typing import Optional
from app.core.models import SimulationResult, TransitionStep, AutomataMetadata


class IValidationService(ABC):
    @abstractmethod
    def validate(self, input_string: str) -> SimulationResult:
        """One-shot validation for the Validator Dashboard."""
        pass


class ISimulationService(ABC):
    @abstractmethod
    def create_session(self, input_string: str) -> str:
        """Initializes a stepping session. Returns session_id."""
        pass

    @abstractmethod
    def step(self, session_id: str) -> Optional[TransitionStep]:
        """Steps forward 1 symbol. Returns None when finished."""
        pass

    @abstractmethod
    def run_all(self, session_id: str) -> SimulationResult:
        """Runs remaining steps to completion."""
        pass

    @abstractmethod
    def reset(self, session_id: str) -> None:
        """Resets session to step 0 and state q0."""
        pass

    @abstractmethod
    def get_metadata(self) -> AutomataMetadata:
        """Returns Minimized DFA formal metadata for Page 3."""
        pass
```

---

## 5. Ten Immutable Team Rules

1. **The Minimized DFA is the Sole Source of Truth:** Never use regex or string heuristics to determine acceptance in the final app.
2. **The GUI Contains Zero Automata Algorithms:** Chester renders results and captures clicks. Transitions happen strictly in `app/core/`.
3. **Backend Code Never Imports PySide6:** Ken's code must remain 100% headless and testable without a window manager.
4. **Shared Contracts Are Frozen Before Implementation:** Ken builds to `models.py`. Chester builds against `mock_service.py`.
5. **No Silent Breaking Changes:** Modifying any method in `models.py` requires unanimous 3-person consent.
6. **Every Feature Requires Automated Tests:** No PR is merged without passing unit tests in `pytest`.
7. **Every Pull Request Explains What Changed:** Include task ID, files touched, and local test proof in PR descriptions.
8. **Integrator Governs Merges; Teammates Own Their Code:** The Integrator reviews and merges, but does not secretly rewrite teammates' logic.
9. **Formal Language Audits Are Mandatory If Rules Change:** If the ID format changes, RE, NFA, DFA, Minimizer, and tests update in lockstep.
10. **All Three Members Must Be Able to Defend the System:** Ken understands the GUI; Chester understands minimization; Integrator understands both.

---

## 6. Documentation Navigation Hub

| Role | Guide File | Primary Focus |
| :--- | :--- | :--- |
| **Ken (Backend Lead)** | [docs/KEN_BACKEND_GUIDE.md](file:///home/nightingale/Desktop/Automata_WTF/docs/KEN_BACKEND_GUIDE.md) | Core Automata, Minimizer, Simulator, Services, pytest |
| **Chester (Frontend Lead)** | [docs/CHESTER_FRONTEND_GUIDE.md](file:///home/nightingale/Desktop/Automata_WTF/docs/CHESTER_FRONTEND_GUIDE.md) | PySide6 Shell, 4 GUI Pages, Custom Widgets, Mock Service |
| **Integrator (Merger / QA)** | [docs/INTEGRATOR_GUIDE.md](file:///home/nightingale/Desktop/Automata_WTF/docs/INTEGRATOR_GUIDE.md) | Git Branching, PR Reviews, Merging, E2E QA, Defense Flow |
