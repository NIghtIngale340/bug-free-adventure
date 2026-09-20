# NFA — Employee ID Validator

**Author:** Ken (Backend / Automata Core Lead)

## 1. Formal Definition

    M_NFA = (Q, Σ, δ, q₀, F)

- **Q** = { q0, q1, …, q13, q_trap }  (15 states)
- **Σ** = { E, M, P, -, 0…9 }  (14 symbols)
- **q₀** = q0
- **F** = { q13 }
- **δ** — transition function below

## 2. Design Note

The Employee ID language is a pure concatenation with no branching and no
ε-transitions. Its minimal NFA is therefore structurally identical to the DFA:
each state has exactly one outgoing symbol class.

The subset construction in `app/core/nfa.py` is implemented in full
generality (ε-closure + multi-target moves) so it still works if the language
is extended later.

## 3. Transition Table

| State | Symbol | Next |
|---|---|---|
| q0  | E | q1 |
| q1  | M | q2 |
| q2  | P | q3 |
| q3  | - | q4 |
| q4  | 0–9 | q5 |
| q5  | 0–9 | q6 |
| q6  | 0–9 | q7 |
| q7  | 0–9 | q8 |
| q8  | - | q9 |
| q9  | 0–9 | q10 |
| q10 | 0–9 | q11 |
| q11 | 0–9 | q12 |
| q12 | 0–9 | q13 |
| q13 | any Σ | q_trap |
| q_trap | any Σ | q_trap |

Any (state, symbol) pair not listed → q_trap.

## 4. State Diagram (text form)

    q0 --E--> q1 --M--> q2 --P--> q3 -----> q4 --d--> q5 --d--> q6 --d--> q7
       --d--> q8 -----> q9 --d--> q10 --d--> q11 --d--> q12 --d--> (q13)  ACCEPT

    Any other symbol at any state --> q_trap (sticky, rejecting)

## 5. Implementation

- `app/core/nfa.py::NFA` — NFA data structure
- `app/core/nfa.py::canonical_nfa` — builds the NFA above
- `app/core/nfa.py::subset_construction` — NFA → DFA conversion

## 6. Verification

`tests/core/test_dfa.py::test_subset_construction_agrees_with_canonical`
proves the resulting DFA accepts exactly the same strings as the canonical one.