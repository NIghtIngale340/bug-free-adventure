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
from typing import Any


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
    final_state: str | None
    trace: list[TransitionStep]
    error_message: str | None
    error_position: int | None
    processed_symbols: int
    total_symbols: int
    explanation: str


@dataclass(frozen=True)
class AutomataMetadata:
    """Formal description of the Minimized DFA for theory display."""
    states: list[str]
    alphabet: list[str]
    start_state: str
    accepting_states: list[str]
    transition_table: dict[str, dict[str, str]]
    re_pattern: str
    minimization_summary: dict[str, Any]
    nfa_summary: dict[str, Any] | None = None