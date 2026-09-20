"""
SHARED DATA CONTRACTS (FROZEN)
Owner: Ken (Backend) — co-reviewed with Integrator

These dataclasses and enums are the immutable bridge between the backend
automata core and Chester's PySide6 GUI.

Per team Rule 5, modifying any signature here requires unanimous
3-person consent.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional


class SimulationStatus(Enum):
    ACCEPTED = "ACCEPTED"
    REJECTED_INVALID_SYMBOL = "REJECTED_INVALID_SYMBOL"
    REJECTED_NON_FINAL_STATE = "REJECTED_NON_FINAL_STATE"
    REJECTED_NO_TRANSITION = "REJECTED_NO_TRANSITION"
    REJECTED_EMPTY_INPUT = "REJECTED_EMPTY_INPUT"


@dataclass(frozen=True)
class TransitionStep:
    """Represents a single symbol transition in the Minimized DFA."""
    step: int
    symbol: str
    from_state: str
    to_state: str
    is_valid: bool
    explanation: str


@dataclass(frozen=True)
class SimulationResult:
    """The complete outcome of an Employee ID validation."""
    input_string: str
    accepted: bool
    status: SimulationStatus
    final_state: Optional[str]
    trace: List[TransitionStep]
    error_message: Optional[str]
    error_position: Optional[int]
    processed_symbols: int
    total_symbols: int
    explanation: str


@dataclass(frozen=True)
class AutomataMetadata:
    """Formal description of the Minimized DFA for theory display."""
    states: List[str]
    alphabet: List[str]
    start_state: str
    accepting_states: List[str]
    transition_table: Dict[str, Dict[str, str]]
    re_pattern: str
    minimization_summary: Dict[str, Any]