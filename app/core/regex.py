"""
FORMAL REGULAR EXPRESSION (AST)

The course's regular expressions use only union, concatenation and (here) bounded
repetition, so a four-node AST is all the project needs. The AST is the single
source of truth for the Employee-ID language: Sigma, the NFA (Thompson
construction in app/core/nfa.py), the DFA and the minimal DFA are all derived
from it. There is deliberately no text parser (nothing needs one).

    Lit('E')                 a single symbol
    Class(('0',..,'9'), 'D') union  (0 ∪ 1 ∪ ... ∪ 9)  collapsed into one atom
    Concat((r1, r2, ...))    r1 · r2 · ...
    Repeat(r, n)             r · r · ... · r   (n copies)
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Lit:
    char: str


@dataclass(frozen=True)
class Class:
    """Union of single symbols, e.g. D = (0 ∪ 1 ∪ ... ∪ 9)."""
    chars: tuple[str, ...]
    name: str = ""


@dataclass(frozen=True)
class Repeat:
    node: "Node"
    n: int


@dataclass(frozen=True)
class Concat:
    parts: tuple["Node", ...]


Node = Lit | Class | Repeat | Concat

_SUPERSCRIPT = str.maketrans("0123456789", "⁰¹²³⁴⁵⁶⁷⁸⁹")


def alphabet_of(node: Node) -> set[str]:
    match node:
        case Lit(c):
            return {c}
        case Class(chars):
            return set(chars)
        case Repeat(inner, _):
            return alphabet_of(inner)
        case Concat(parts):
            return set().union(*(alphabet_of(p) for p in parts))


def length_of(node: Node) -> int:
    """Length of every word in L(node) (fixed for this RE family)."""
    match node:
        case Lit() | Class():
            return 1
        case Repeat(inner, n):
            return n * length_of(inner)
        case Concat(parts):
            return sum(length_of(p) for p in parts)


def formal(node: Node) -> str:
    """Compact formal notation, e.g. EMP-D⁴-D⁴ (named classes stay abbreviated)."""
    match node:
        case Lit(c):
            return c
        case Class(chars, name):
            return name or "(" + "∪".join(chars) + ")"
        case Repeat(inner, n):
            return formal(inner) + str(n).translate(_SUPERSCRIPT)
        case Concat(parts):
            return "".join(formal(p) for p in parts)


def expanded(node: Node) -> str:
    """Repetition unrolled and concatenation shown with '·': E·M·P·-·D·D·D·D·-·D·D·D·D."""
    def atoms(n: Node) -> list[str]:
        match n:
            case Lit(c):
                return [c]
            case Class(chars, name):
                return [name or "(" + "∪".join(chars) + ")"]
            case Repeat(inner, k):
                return atoms(inner) * k
            case Concat(parts):
                return [a for p in parts for a in atoms(p)]
    return "·".join(atoms(node))


def definitions(node: Node) -> dict[str, str]:
    """Named classes used by the RE: {'D': '(0∪1∪…∪9)'}."""
    out: dict[str, str] = {}
    match node:
        case Class(chars, name) if name:
            out[name] = "(" + "∪".join(chars) + ")"
        case Repeat(inner, _):
            out.update(definitions(inner))
        case Concat(parts):
            for p in parts:
                out.update(definitions(p))
    return out
