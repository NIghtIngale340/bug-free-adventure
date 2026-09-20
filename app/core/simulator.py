"""
MINIMIZED DFA SIMULATOR & TRACE ENGINE
Owner: Ken (Backend / Automata Core Lead)
Task: BE-005

Runs an input string through the Minimized DFA symbol-by-symbol and
produces a complete SimulationResult for Chester's GUI to render.

This module is the ONLY place where acceptance is decided.
"""

from typing import List, Optional

from app.core.dfa import DFA
from app.core.language import is_symbol_in_alphabet
from app.core.models import (
    SimulationResult,
    SimulationStatus,
    TransitionStep,
)
from app.data.id_rules import START_STATE, TRAP_STATE


def simulate(input_string: str, dfa: Optional[DFA] = None) -> SimulationResult:
    """
    Run `input_string` through the Minimized DFA and return a structured
    SimulationResult.

    Rules:
      - Empty input      -> REJECTED_EMPTY_INPUT, final_state=None
      - Symbol outside Σ -> REJECTED_INVALID_SYMBOL, stops at that index
      - No valid move    -> transition to q_trap, REJECTED_NO_TRANSITION
      - Ends in q13      -> ACCEPTED
      - Ends elsewhere   -> REJECTED_NON_FINAL_STATE
    """
    dfa = dfa or DFA()
    trace: List[TransitionStep] = []
    total = len(input_string)

    # --- Layer 1a: empty input ------------------------------------------
    if total == 0:
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

    state = dfa.start_state

    # --- Layer 1b + Layer 2: alphabet check, then DFA stepping ----------
    for idx, symbol in enumerate(input_string):
        step_no = idx + 1

        # If symbol is not in Σ, reject immediately.
        if not is_symbol_in_alphabet(symbol):
            trace.append(
                TransitionStep(
                    step=step_no,
                    symbol=symbol,
                    from_state=state,
                    to_state=TRAP_STATE,
                    is_valid=False,
                    explanation=(
                        f"Symbol {symbol!r} is outside the alphabet Sigma."
                    ),
                )
            )
            return SimulationResult(
                input_string=input_string,
                accepted=False,
                status=SimulationStatus.REJECTED_INVALID_SYMBOL,
                final_state=TRAP_STATE,
                trace=trace,
                error_message=(
                    f"Invalid symbol {symbol!r} at position {idx}."
                ),
                error_position=idx,
                processed_symbols=step_no,
                total_symbols=total,
                explanation=(
                    f"Rejected: {symbol!r} is not part of the Employee ID alphabet."
                ),
            )

        # Valid symbol: attempt the DFA transition.
        next_state = dfa.step(state, symbol)
        is_valid = next_state != TRAP_STATE or state == TRAP_STATE

        if state == TRAP_STATE:
            explanation = "Already in trap state; input is rejected."
            is_valid = False
        elif next_state == TRAP_STATE:
            explanation = (
                f"No valid transition from {state} on {symbol!r}."
            )
        else:
            explanation = f"{state} --{symbol}--> {next_state}"

        trace.append(
            TransitionStep(
                step=step_no,
                symbol=symbol,
                from_state=state,
                to_state=next_state,
                is_valid=is_valid,
                explanation=explanation,
            )
        )
        state = next_state

        # Short-circuit: once trapped, no need to keep consuming symbols.
        if state == TRAP_STATE:
            return SimulationResult(
                input_string=input_string,
                accepted=False,
                status=SimulationStatus.REJECTED_NO_TRANSITION,
                final_state=TRAP_STATE,
                trace=trace,
                error_message=(
                    f"Invalid transition on symbol {symbol!r} at position {idx}."
                ),
                error_position=idx,
                processed_symbols=step_no,
                total_symbols=total,
                explanation=(
                    f"Rejected: transition to trap on {symbol!r} at position {idx}."
                ),
            )

    # --- Layer 3: final decision ----------------------------------------
    accepted = dfa.is_accepting(state)
    if accepted:
        status = SimulationStatus.ACCEPTED
        explanation = "Input recognized as a valid Employee ID."
        error_message = None
        error_position = None
    else:
        status = SimulationStatus.REJECTED_NON_FINAL_STATE
        explanation = (
            f"Rejected: ended in state {state}, which is not accepting."
        )
        error_message = (
            f"Input ended in non-accepting state {state}."
        )
        error_position = None

    return SimulationResult(
        input_string=input_string,
        accepted=accepted,
        status=status,
        final_state=state,
        trace=trace,
        error_message=error_message,
        error_position=error_position,
        processed_symbols=total,
        total_symbols=total,
        explanation=explanation,
    )