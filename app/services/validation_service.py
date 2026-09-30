"""
ONE-SHOT VALIDATION SERVICE

    ValidationService.validate(input_string) -> SimulationResult

Thin facade over app.core.simulator.simulate() on the minimal DFA.
"""

from app.core.models import SimulationResult
from app.core.simulator import simulate


class ValidationService:
    def validate(self, input_string: str) -> SimulationResult:
        return simulate(input_string)
