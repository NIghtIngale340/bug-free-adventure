"""
FORMAL LANGUAGE & ALPHABET (Layer 1 of the validation pipeline)

Layer 1  alphabet check  : is every symbol of the input in Sigma?   (this module)
Layer 2  automaton run   : symbol-by-symbol on the DFA / NFA        (app/core/simulator.py)
Layer 3  presentation    : ACCEPTED / REJECTED + explanation        (GUI)

Sigma is ASCII-only: full-width digits, Arabic-Indic digits, look-alike hyphens and
Cyrillic homoglyphs are all outside Sigma.
"""

from app.data.id_rules import ALPHABET, DIGITS, RE_PATTERN, TOTAL_LENGTH


def is_symbol_in_alphabet(char: str) -> bool:
    """True iff `char` is a single symbol belonging to Sigma."""
    return len(char) == 1 and char in ALPHABET


def validate_symbols(input_str: str) -> tuple[bool, list[tuple[int, str]]]:
    """(True, []) if every symbol is in Sigma, else (False, [(index, char), ...])."""
    illegal = [(i, ch) for i, ch in enumerate(input_str) if ch not in ALPHABET]
    return not illegal, illegal


def describe_symbols(symbols: list[str]) -> str:
    """Human wording for a set of expected symbols: "a digit 0–9", "'-'", "'E' or 'M'"."""
    rest = sorted(set(symbols) - set(DIGITS))
    parts = (["a digit 0–9"] if set(DIGITS) <= set(symbols) else [f"'{d}'" for d in sorted(set(symbols) & set(DIGITS))])
    parts += [f"'{c}'" for c in rest]
    return " or ".join(parts) if parts else "end of input"


def describe_language() -> dict:
    """JSON-friendly summary of the formal language for docs / metadata."""
    return {
        "format": "EMP-YYYY-NNNN",
        "alphabet": sorted(ALPHABET),
        "alphabet_size": len(ALPHABET),
        "total_length": TOTAL_LENGTH,
        "regex": RE_PATTERN,
    }
