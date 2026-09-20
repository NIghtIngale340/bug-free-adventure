"""
FORMAL LANGUAGE & ALPHABET VALIDATOR
Owner: Ken (Backend / Automata Core Lead)
Task: BE-001

Responsibilities:
  - Expose Sigma (the alphabet) as a Python set.
  - Provide is_symbol_in_alphabet(char) -> bool
  - Provide validate_symbols(input_str) -> (ok, errors)
    where errors is a list of (index, char) for symbols outside Sigma.

Layer 1 of the validation pipeline (alphabet check).
Layer 2 (automata simulation) lives in app/core/simulator.py.
"""


from app.data.id_rules import ALPHABET, RE_PATTERN, TOTAL_LENGTH


def is_symbol_in_alphabet(char: str) -> bool:
    """Return True iff `char` is a single symbol belonging to Sigma."""
    return len(char) == 1 and char in ALPHABET


def validate_symbols(input_str: str) -> tuple[bool, list[tuple[int, str]]]:
    """
    Check every character against Sigma.

    Returns:
        (True,  [])                if all symbols belong to Sigma
        (False, [(idx, char), ...]) otherwise
    """
    illegal: list[tuple[int, str]] = []
    for idx, ch in enumerate(input_str):
        if not is_symbol_in_alphabet(ch):
            illegal.append((idx, ch))
    return (len(illegal) == 0), illegal


def describe_language() -> dict:
    """Return a JSON-friendly summary of the formal language for docs / metadata."""
    return {
        "format": "EMP-YYYY-NNNN",
        "alphabet": sorted(ALPHABET),
        "alphabet_size": len(ALPHABET),
        "total_length": TOTAL_LENGTH,
        "regex": RE_PATTERN,
    }