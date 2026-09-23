from dataclasses import dataclass
from enum import Enum
from typing import Optional


class SimulationStatus(Enum):
    ACCEPTED = "ACCEPTED"
    REJECTED_EMPTY_INPUT = "REJECTED_EMPTY_INPUT"
    REJECTED_INVALID_SYMBOL = "REJECTED_INVALID_SYMBOL"
    REJECTED_NON_FINAL_STATE = "REJECTED_NON_FINAL_STATE"
    REJECTED_TRAP_STATE = "REJECTED_TRAP_STATE"


@dataclass
class TransitionStep:
    step: int
    symbol: str
    from_state: str
    to_state: str
    is_valid: bool
    description: str


@dataclass
class SimulationResult:
    input_string: str
    accepted: bool
    status: SimulationStatus
    final_state: Optional[str]
    trace: list[TransitionStep]
    error_message: Optional[str]
    error_position: Optional[int]
    processed_symbols: int
    total_symbols: int
    explanation: str


@dataclass
class AutomataMetadata:
    states: list[str]
    alphabet: list[str]
    start_state: str
    accepting_states: list[str]
    transition_table: dict
    re_pattern: str
    minimization_summary: dict