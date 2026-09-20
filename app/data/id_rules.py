"""
CANONICAL ID RULES, ALPHABET, AND MINIMIZED DFA TRANSITION TABLE
Owner: Ken (Backend / Automata Core Lead)

Single source of truth for the Employee ID formal language.

Language: L = { w in Sigma* | w = EMP-YYYY-NNNN }
  - Prefix: 'EMP'
  - Separator 1: '-'
  - Year: 4 digits [0-9]
  - Separator 2: '-'
  - Sequence: 4 digits [0-9]
  - Total length: exactly 13 characters

Alphabet (|Sigma| = 14):
  Sigma = {'E', 'M', 'P', '-', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9'}
"""

from typing import Dict, FrozenSet, List

# --- Alphabet ---------------------------------------------------------------

DIGITS: List[str] = [str(d) for d in range(10)]  # '0' .. '9'

ALPHABET: FrozenSet[str] = frozenset({"E", "M", "P", "-", *DIGITS})

# --- Language structure -----------------------------------------------------

PREFIX: str = "EMP"
TOTAL_LENGTH: int = 13

# Regular expression (documentation + metadata, NOT used for acceptance).
# Per team Rule 1, the Minimized DFA is the only source of truth.
RE_PATTERN: str = r"^EMP-[0-9]{4}-[0-9]{4}$"

# --- Canonical Minimized DFA (Q, Sigma, delta, q0, F) ----------------------

START_STATE: str = "q0"
TRAP_STATE: str = "q_trap"
ACCEPTING_STATES: FrozenSet[str] = frozenset({"q13"})

CANONICAL_STATES: List[str] = [
    "q0", "q1", "q2", "q3", "q4", "q5", "q6", "q7",
    "q8", "q9", "q10", "q11", "q12", "q13", TRAP_STATE,
]

CANONICAL_TRANSITIONS: Dict[str, Dict[str, str]] = {
    "q0":  {"E": "q1"},
    "q1":  {"M": "q2"},
    "q2":  {"P": "q3"},
    "q3":  {"-": "q4"},
    "q4":  {d: "q5"  for d in DIGITS},
    "q5":  {d: "q6"  for d in DIGITS},
    "q6":  {d: "q7"  for d in DIGITS},
    "q7":  {d: "q8"  for d in DIGITS},
    "q8":  {"-": "q9"},
    "q9":  {d: "q10" for d in DIGITS},
    "q10": {d: "q11" for d in DIGITS},
    "q11": {d: "q12" for d in DIGITS},
    "q12": {d: "q13" for d in DIGITS},
    "q13": {},
    TRAP_STATE: {},
}