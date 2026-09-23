# Regular Expression — Employee ID Validator

**Author:** Ken (Backend / Automata Core Lead)

## 1. The Regular Expression

    RE = EMP-[0-9]{4}-[0-9]{4}

Python form (with anchors):

    ^EMP-[0-9]{4}-[0-9]{4}$

## 2. Component Breakdown

| Component | Meaning |
|---|---|
| `E`, `M`, `P` | Literal uppercase prefix |
| `-` | First hyphen |
| `[0-9]{4}` | Exactly four decimal digits (year) |
| `-` | Second hyphen |
| `[0-9]{4}` | Exactly four decimal digits (sequence) |
| `^` | Anchor at start |
| `$` | Anchor at end |

## 3. Why the Anchors Matter

Without `^` and `$`, `EMP-2026-0042-EXTRA` would match. The anchors force the
entire string to belong to L.

## 4. Length

    |w| = 3 + 1 + 4 + 1 + 4 = 13

consistent with the DFA's 13-step path from q₀ to q₁₃.

## 5. Relation to the Automaton

By Kleene's theorem, every RE has an equivalent NFA, and every NFA has an
equivalent DFA. This project follows the full pipeline:

    RE  →  NFA  →  DFA  →  Minimized DFA  →  Python simulator

Per team Rule 1, **the RE is documentation only**. Acceptance in the program
is decided strictly by the Minimized DFA in `app/core/dfa.py`.