# DFA — Employee ID Validator

**Author:** Ken (Backend / Automata Core Lead)

## 1. Formal Definition

    M_DFA = (Q, Σ, δ, q₀, F)

- **Q** = { q0, q1, …, q13, q_trap }  (15 states)
- **Σ** = { E, M, P, -, 0…9 }  (14 symbols)
- **q₀** = q0
- **F** = { q13 }
- **δ** = `CANONICAL_TRANSITIONS` in `app/data/id_rules.py`

## 2. Subset Construction Trace

Because the NFA is branch-free, subset construction produces a DFA
isomorphic to the NFA:

| DFA State | NFA Subset | Meaning |
|---|---|---|
| D0  | {q0}  | start |
| D1  | {q1}  | after E |
| D2  | {q2}  | after M |
| D3  | {q3}  | after P |
| D4  | {q4}  | after first hyphen |
| D5  | {q5}  | after year digit 1 |
| D6  | {q6}  | after year digit 2 |
| D7  | {q7}  | after year digit 3 |
| D8  | {q8}  | after year digit 4 |
| D9  | {q9}  | after second hyphen |
| D10 | {q10} | after seq digit 1 |
| D11 | {q11} | after seq digit 2 |
| D12 | {q12} | after seq digit 3 |
| D13 | {q13} | accepting |
| D_trap | {q_trap} | dead |

## 3. Transition Table

See `AUTOMATA_THEORY_BASELINE.md` §3 for the full table.

## 4. Determinism

For every state q and every symbol a ∈ Σ, there is exactly one next state
δ(q, a). If δ is not explicitly defined, the canonical implementation treats
it as a move to q_trap.

## 5. Acceptance Rule

A string w is accepted iff, after consuming every symbol, the DFA is in a
state of F = {q13}.

## 6. Implementation

- `app/core/dfa.py::DFA` — the DFA class (`step`, `run`, `accepts`)
- `app/data/id_rules.py::CANONICAL_TRANSITIONS` — δ table

## 7. Verification

`tests/core/test_dfa.py` covers accepted standard IDs, boundaries,
structural rejections, trap stickiness, and agreement with the DFA
produced by subset construction.