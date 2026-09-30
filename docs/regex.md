# Regular Expression — Employee ID Validator

## 1. The regular expression

<!-- BEGIN generated:regex-line -->
`EMP-D⁴-D⁴` = `E·M·P·-·D·D·D·D·-·D·D·D·D`, where D = (0∪1∪2∪3∪4∪5∪6∪7∪8∪9)
<!-- END generated:regex-line -->

Only the operators of the course are used: union `∪`, concatenation `·` and bounded repetition
(superscript = that many copies). `D` is shorthand for the union of the ten digits.

## 2. Components

| Position | Component | Meaning | Matches | Rejects |
|---|---|---|---|---|
| 1–3 | `E·M·P` | fixed uppercase prefix | `EMP` | `emp`, `EM`, `AXP` |
| 4 | `-` | first separator | `-` | `_`, missing |
| 5–8 | `D⁴` | exactly four digits (the year `YYYY`) | `2026` | `26`, `20261`, `202A` |
| 9 | `-` | second separator | `-` | `--`, missing |
| 10–13 | `D⁴` | exactly four digits (the employee number `NNNN`) | `0042` | `123`, `00001`, `12B4` |

Length: 3 + 1 + 4 + 1 + 4 = 13, matching the 13 steps from `q0` to `q13`.
In the application these parts appear as coloured bars under the input tape (Simulate) and in the Theory → Regular expression tab.

## 3. Formal RE vs. the Python pattern

The Python-style pattern `EMP-[0-9]{4}-[0-9]{4}` (in `app/data/id_rules.py::RE_PATTERN`) denotes the same
language, but it uses shorthand (`[0-9]`, `{4}`) that is not part of the course's RE notation. It is used
**only as a test oracle**, always with `re.fullmatch`: the anchored form `^…$` would wrongly accept
`"EMP-2026-0001\n"` because `$` matches before a trailing newline. Acceptance in the application is decided
solely by the minimal DFA.

## 4. From RE to automaton

`ID_REGEX` is an AST (`app/core/regex.py`). `thompson()` (`app/core/nfa.py`) turns it into an ε-NFA
([nfa.md](nfa.md)); subset construction turns that into a DFA ([dfa.md](dfa.md)); minimization yields the
recognizer the simulator runs ([minimization.md](minimization.md)).
