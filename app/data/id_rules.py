"""
EMPLOYEE-ID LANGUAGE DEFINITION

Single source of truth:  ID_REGEX  (a formal regular expression).
Sigma, the NFA, the DFA and the minimal DFA are all *derived* from it in
app/core/pipeline.py; nothing below is executed by the simulator except ID_REGEX.

    L = { w in Sigma* | w = EMP-YYYY-NNNN },  D = (0 ∪ 1 ∪ ... ∪ 9)
    RE = E·M·P·-·D·D·D·D·-·D·D·D·D   =   EMP-D⁴-D⁴
    |w| = 13 for every w in L,  |L| = 10^8  (a finite, hence regular, language)
"""

from dataclasses import dataclass

from app.core.regex import Class, Concat, Lit, Repeat, alphabet_of, formal, length_of

DIGITS: list[str] = [str(d) for d in range(10)]  # '0' .. '9'

DIGIT = Class(tuple(DIGITS), name="D")
# The RE as named parts (the names only label the tape and the docs; the RE is the concatenation).
_PARTS = (
    ("prefix", Concat((Lit("E"), Lit("M"), Lit("P")))),
    ("separator", Lit("-")),
    ("year YYYY", Repeat(DIGIT, 4)),      # any four digits (syntactic check only, no year range)
    ("separator", Lit("-")),
    ("number NNNN", Repeat(DIGIT, 4)),
)
ID_REGEX = Concat(tuple(node for _, node in _PARTS))


@dataclass(frozen=True)
class Segment:
    """Positions [start, end) of an input that one part of the RE matches."""
    name: str
    formal: str
    start: int
    end: int


def _segments() -> tuple[Segment, ...]:
    out, pos = [], 0
    for name, node in _PARTS:
        out.append(Segment(name, formal(node), pos, pos + length_of(node)))
        pos += length_of(node)
    return tuple(out)


ID_SEGMENTS: tuple[Segment, ...] = _segments()

ALPHABET: frozenset[str] = frozenset(alphabet_of(ID_REGEX))
TOTAL_LENGTH: int = length_of(ID_REGEX)

# Same language in PCRE shorthand. Documentation and TEST ORACLE ONLY (use re.fullmatch:
# '^...$' would wrongly accept a trailing newline). Never used for acceptance.
RE_PATTERN: str = r"EMP-[0-9]{4}-[0-9]{4}"

# Naming convention for the derived minimal DFA.
TRAP_STATE: str = "q_trap"

# --- Hand-written reference automaton --------------------------------------
# Used ONLY by tests / the Equivalence tab to cross-check the derived minimal DFA.
# The simulator never reads it.
REFERENCE_START = "q0"
REFERENCE_ACCEPTING = frozenset({"q13"})
REFERENCE_STATES: list[str] = [f"q{i}" for i in range(14)] + [TRAP_STATE]
REFERENCE_TRANSITIONS: dict[str, dict[str, str]] = {
    "q0": {"E": "q1"}, "q1": {"M": "q2"}, "q2": {"P": "q3"}, "q3": {"-": "q4"},
    **{f"q{i}": {d: f"q{i + 1}" for d in DIGITS} for i in (4, 5, 6, 7)},
    "q8": {"-": "q9"},
    **{f"q{i}": {d: f"q{i + 1}" for d in DIGITS} for i in (9, 10, 11, 12)},
    "q13": {}, TRAP_STATE: {},
}
