# Formal Language Definition — Employee ID Validator

**Author:** Ken (Backend / Automata Core Lead)
**Course:** CCAUTOMA — 1st AY 2026

## 1. Problem Statement

An organization defines its Employee ID format as:

    EMP-YYYY-NNNN

- `EMP` — fixed uppercase prefix
- `-` — first hyphen separator
- `YYYY` — four-digit year `[0-9]{4}`
- `-` — second hyphen separator
- `NNNN` — four-digit sequence number `[0-9]{4}`

The recognizer must accept exactly the strings following this structure.

## 2. Alphabet Σ

    Σ = { E, M, P, -, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9 }
    |Σ| = 14

Any character outside Σ causes immediate rejection with
`REJECTED_INVALID_SYMBOL`.

## 3. Language L

    L = { w ∈ Σ* | w = EMP-d₁d₂d₃d₄-d₅d₆d₇d₈, dᵢ ∈ {0,…,9} }

Every string in L has length exactly 13. L is a **regular language** because
it can be described by a finite regular expression and recognized by a
15-state DFA.

## 4. Accepted Strings (≥ 10)

| # | String |
|---|---|
| 1 | EMP-2026-0001 |
| 2 | EMP-2026-0042 |
| 3 | EMP-2026-9999 |
| 4 | EMP-2000-0000 |
| 5 | EMP-2099-9999 |
| 6 | EMP-1999-5555 |
| 7 | EMP-2024-8765 |
| 8 | EMP-2025-0101 |
| 9 | EMP-2027-3333 |
| 10 | EMP-2030-7777 |

## 5. Rejected Strings (≥ 10)

| # | String | Reason |
|---|---|---|
| 1 | EMP2026-0001 | Missing first hyphen |
| 2 | EMP-26-0001 | Year too short |
| 3 | EMP-2026-123 | Sequence too short |
| 4 | emp-2026-0001 | Lowercase prefix (outside Σ) |
| 5 | EMP-2026-12A4 | `A` outside Σ |
| 6 | EMP-2026-00001 | Sequence too long |
| 7 | EMP_2026_0001 | Underscore instead of hyphen |
| 8 | EMP--2026-0001 | Double hyphen |
| 9 | EMP-2026-00!1 | `!` outside Σ |
| 10 | EMP-2026-0001␣ | Trailing space |
| 11 | ␣EMP-2026-0001 | Leading space |
| 12 | (empty) | Empty input |

## 6. Why This is a Regular Language

- Expressible as a finite RE.
- Recognized by a 15-state DFA with no unbounded memory.
- Requires no stack and no counter.

## 7. Implementation

- `app/data/id_rules.py` — ALPHABET, CANONICAL_TRANSITIONS
- `app/core/language.py` — validate_symbols, is_symbol_in_alphabet
- `app/core/simulator.py` — simulate (the recognizer)

All rejected strings above are covered by automated tests.