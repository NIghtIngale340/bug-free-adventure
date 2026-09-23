"""
ONE-SHOT VALIDATION SERVICE
Owner: Ken (Backend / Automata Core Lead)
Task: BE-006

Public contract (frozen — see SHARED_ARCHITECTURE_AND_CONTRACTS.md):
    ValidationService.validate(input_string: str) -> SimulationResult

Used by: Chester's Page 1 (Validator Dashboard).
"""

from app.core.models import SimulationResult
from app.core.simulator import simulate


class ValidationService:
    """Thin facade over app.core.simulator.simulate()."""

    def validate(self, input_string: str) -> SimulationResult:
        return simulate(input_string)