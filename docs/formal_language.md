# Formal Language Definition — Employee ID Validator

**Course:** CCAUTOMA — 1st AY 2026

## 1. Problem definition

An organization issues employee IDs of the form `EMP-YYYY-NNNN`. HR staff type IDs by hand, and the
validator decides whether a typed string is a well-formed ID and shows *how* the automaton reached
its decision (state by state).

- **Intended users:** HR / administrative staff entering IDs; the panel and classmates studying the automaton.
- **Input:** any string the user types — any characters, any length (including empty).
- **Valid input:** a string in the language `L` below.
- **Invalid input:** every other string, including strings containing characters outside Σ.

Format: `EMP` (fixed uppercase prefix) · `-` · `YYYY` (four digits) · `-` · `NNNN` (four digits).
`YYYY` is *any* four digits — the language checks syntax, not that the year is plausible.

## 2. Alphabet Σ

```text
Σ = { E, M, P, -, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9 }      |Σ| = 14
```

Σ is ASCII-only. Lowercase letters, spaces, `_`, full-width or Arabic-Indic digits, look-alike hyphens
and Cyrillic homoglyphs are all **outside** Σ. A string containing any such symbol is not a string over Σ
and is rejected by Layer 1 (see [architecture.md](architecture.md)) before the automaton runs.

## 3. Language L

```text
L = { w ∈ Σ* | w = E M P - d₁d₂d₃d₄ - d₅d₆d₇d₈,  dᵢ ∈ {0,…,9} }
```

Every word has length exactly 13, and |L| = 10⁸.

## 4. Why a finite automaton

`L` is finite, hence regular (every finite language is). Recognizing it needs no unbounded memory,
no counter and no stack: a DFA that counts symbols 0…13 (15 states including a dead state) suffices.

## 5. Accepted and rejected examples

Accepted:

<!-- BEGIN generated:accepted -->
| String | Note |
|---|---|
| `EMP-2026-0001` | Standard valid ID |
| `EMP-2026-0042` | Standard valid ID |
| `EMP-2026-9999` | Maximum sequence number |
| `EMP-2000-0000` | Boundary year 2000 |
| `EMP-2099-1234` | Boundary year 2099 |
| `EMP-1999-5555` | Historical year 1999 |
| `EMP-2024-8765` | Recent year 2024 |
| `EMP-2025-0101` | Valid sequence |
| `EMP-2027-3333` | Future year 2027 |
| `EMP-2030-7777` | Future year 2030 |
<!-- END generated:accepted -->

Rejected:

<!-- BEGIN generated:rejected -->
| String | Reason rejected |
|---|---|
| `AXP-2026-0001` | Prefix is not 'EMP' |
| `emp-2026-0001` | Prefix must be uppercase |
| `EM-2026-0001` | Prefix too short |
| `EMPP-2026-0001` | Prefix too long |
| `EMP2026-0001` | Missing first hyphen |
| `EMP-20260001` | Missing second hyphen |
| `EMP_2026_0001` | Underscore instead of hyphen |
| `EMP--2026-0001` | Consecutive hyphens |
| `EMP-26-0001` | Year too short (2 digits) |
| `EMP-20261-0001` | Year too long (5 digits) |
| `EMP-202A-0001` | Non-numeric character in year |
| `EMP-2026-1` | Sequence too short |
| `EMP-2026-00001` | Sequence too long |
| `EMP-2026-12B4` | Letter inside numeric sequence |
| `(empty)` | Empty input string |
| `'EMP-2026-0001 '` | Trailing space character |
| `' EMP-2026-0001'` | Leading space character |
| `EMP-2026-00!1` | Symbol '!' outside alphabet Sigma |
<!-- END generated:rejected -->

## 6. Where this lives in the code

- `app/data/id_rules.py` — `ID_REGEX` (single source of truth), `ALPHABET`.
- `app/core/language.py` — Layer 1 alphabet check.
- `app/core/pipeline.py` — derives NFA, DFA and minimal DFA from `ID_REGEX`.
