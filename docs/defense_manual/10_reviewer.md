# 10 — "Everything We Should Know" Reviewer

[← 09 Q&A Bank](09_qa_bank.md) · [Index](README.md)

Every number below was checked against the code on 2026-10-08.

---

## Must-memorize facts

| Fact | Value |
|---|---|
| Format | `EMP-YYYY-NNNN` |
| Alphabet | Σ = {E, M, P, -, 0–9}, **\|Σ\| = 14** (ASCII only) |
| Length of every valid ID | **13** |
| Number of valid IDs | **\|L\| = 10⁸** (100,000,000) |
| Regex | `EMP-D⁴-D⁴`, D = (0∪1∪…∪9) |
| ε-NFA (Thompson) | **26 states** (n0…n25), **12 ε-transitions**, start n0, accept n25 |
| DFA (Rabin–Scott subset construction) | **15 states** = 14 live (D0…D13) + D_trap |
| Minimization (Moore partition refinement) | **15 → 15**, **13 rounds**, **0 merges** |
| Equivalence (product automaton BFS) | **15 state pairs**, **0 discrepancies** → EQUAL |
| Exhaustive differential test | **41,371** strings (all strings of length ≤ 4 over Σ = 1+14+196+2,744+38,416) |
| Randomized differential test | **20,000** strings (valid, mutated, random, Unicode look-alikes), 0 disagreements |
| Mutation test (from code, not on slides) | all **2,940** single-transition mutants of the minimal DFA are caught |
| Predefined suite | **28** cases: 10 valid, 18 invalid, all pass |
| Automated tests | **250+** (279 at last run) |
| GUI pages | Simulate · Theory (8 tabs) · Tests |
| Shortcuts | Space play/pause · → step · ← back · Ctrl+R reset |

## Must-understand concepts

- **Finite ⇒ regular.** Any finite set of strings is a union of single strings, and regular languages are closed under union. (Regular does NOT imply finite.)
- **ε-transition:** a move that reads no symbol. Thompson uses them to glue fragments together.
- **ε-closure(S):** every state reachable from S by ε-moves alone.
- **move(S, a):** every state reachable from S by reading `a` once.
- **Subset construction:** each DFA state = a *set* of NFA states. New state = ε-closure(move(S, a)). Empty set = trap.
- **Total δ:** every state has exactly one move for each of the 14 symbols (15 × 14 = 210 entries).
- **Two states are equivalent** iff exactly the same suffixes lead to acceptance from both.
- **Distance to acceptance:** from Dᵢ the shortest accepted suffix has length 13 − i, and from the trap it's ∞. All 15 distances differ, so no two states are equivalent, so the DFA is minimal.
- **Zero merges is a result, not a failure.** Minimization *proves* minimality. It would merge states if the regex changed and redundancy appeared (tested on a redundant DFA in `tests/core/test_minimization.py`).
- **Formal proof ≠ testing.** Product BFS proves subset DFA ≡ minimal DFA. Differential tests against `re.fullmatch` check that our language matches an independent reference on concrete inputs.
- **Two rejection modes:** symbols outside Σ are rejected *before* the automaton (Layer 1). Wrong order of valid symbols is rejected *inside* the DFA (trap state).

## Must-know examples

| Input | Result | Status | Where it fails |
|---|---|---|---|
| `EMP-2026-0042` | ACCEPT | `ACCEPTED` | ends in q13 after 13/13 symbols |
| `EMP2026-0001` | REJECT | `REJECTED_NO_TRANSITION` | q3 expects `-`, reads `2` at position 3 → q_trap |
| `EMP-2026-12A4` | REJECT | `REJECTED_INVALID_SYMBOL` | `A` ∉ Σ at position 11; automaton never starts |
| `' EMP-2026-0001'` / `'EMP-2026-0001 '` | REJECT | `REJECTED_INVALID_SYMBOL` | space ∉ Σ (position 0 / 13). The GUI never trims input. |
| `emp-2026-0001` | REJECT | `REJECTED_INVALID_SYMBOL` | `e`, `m`, `p` ∉ Σ |
| `EMP-2026-1` | REJECT | `REJECTED_NON_FINAL_STATE` | input ends in q10, needs 3 more digits |
| (empty) | REJECT | `REJECTED_EMPTY_INPUT` | "Please enter an Employee ID." |
| `EMP-0000-0000` | ACCEPT | `ACCEPTED` | year is syntax only, no range check |

Positions are **0-based** (Python indices).

## Must-know proofs

**Minimality (no-merge proof):**
1. P₀ = {{D13}, {everything else}}: accepting vs non-accepting.
2. Each refinement round splits off one more state, working backwards from D13: D12, then D11, …
3. After 13 rounds every block is a singleton, so nothing merges.
4. Why: d(Dᵢ, F) = 13 − i are all distinct, and d(trap) = ∞. If two states had different shortest accepting distances, the shorter suffix is accepted from one and not the other, so the states are distinguishable.

**Equivalence (product automaton):**
1. Run both DFAs side by side. The state is a pair (p, q). Start at (D0, q0).
2. BFS over every reachable pair, trying every symbol in Σ.
3. If any reachable pair has exactly one accepting component, the languages differ (and BFS returns the shortest counterexample).
4. 15 pairs reached, none disagree, so L(subset DFA) = L(minimal DFA). This covers *all* strings, not a sample.

## Must-know architecture

```text
app/gui/        Simulate · Theory · Tests pages        ← draws results only, no automata logic
app/services/   SimulationService · ValidationService  ← packages results for the GUI
app/core/       regex.py  nfa.py  dfa.py  minimizer.py  equivalence.py  pipeline.py  simulator.py
app/data/       id_rules.py (ID_REGEX = single source of truth, Σ)   test_cases.py (28 cases)
```

- `pipeline.py::build_pipeline`: regex → thompson → subset_construction → minimize → dfa_equivalent.
- `simulator.py::Run`: the **one** engine for batch validation, stepping and GUI animation.
- Validation layers: (1) alphabet filter, (2) automaton traversal, (3) result packaging.

## Must-know demo steps

1. Before: `python -m app.main` running, Simulate page open. Tests tab pre-run (28/28). Theory → Equivalence → *Run exhaustive check* pre-run once.
2. Type `EMP-2026-0042` → Enter → Play (or Step). Point at tape, amber edge, state number. Ends in q13 → **ACCEPTED**.
3. Type `EMP2026-0001` → Enter → Step ×4. q3 reads `2` → dashed red edge to q_trap → **REJECTED at position 3**.
4. Type `EMP-2026-12A4` → Enter. Rejected immediately, no state visited → **`'A'` at position 11**.
5. Theory page: show ε-NFA / Subset construction / Minimization tabs.
6. Tests page: "28 / 28 passed · NFA, DFA and minimal DFA agree on 28 / 28". Theory → Equivalence: 41,371 words, 0 disagreements.
7. Fallback if the app misbehaves: screenshots in `assets/screenshots/` and slide 10.

## Top 20 questions (owner in brackets)

1. **Why is the language regular?** [Mark] It's finite (10⁸ strings), and every finite language is regular.
2. **Why not just use Python `re`?** [Chester] `re` is a black box. Our goal is an inspectable, algorithmically derived automaton. We use `re.fullmatch` only as an independent test oracle.
3. **Why did minimization merge zero states?** [Chester] Each state has a different shortest distance to acceptance (13 − i, trap ∞), so all are distinguishable.
4. **Then why run minimization at all?** [Chester] It turns "we think it's minimal" into a verified result, and it would catch redundancy if the regex changed.
5. **Why 15 DFA states?** [Chester] One live state per number of symbols read correctly, 0 to 13, plus the trap.
6. **Why 26 NFA states and 12 ε-transitions?** [Chester] 13 atoms × 2 states = 26; 13 atoms joined in sequence need 12 ε-edges.
7. **Is your NFA really nondeterministic?** [Chester] It's an ε-NFA (12 ε-moves). For this language the ε-closures happen to be deterministic, so the DFA is a chain. The code also handles truly nondeterministic NFAs (tested).
8. **Why an explicit trap state?** [Chester] It makes δ total over Σ, so every input ends in a defined state and the GUI can show exactly where it failed.
9. **Why reject `A` before the DFA instead of sending it to the trap?** [Mark] The DFA is defined over Σ. `A` has no transition by definition. Filtering first keeps δ honest and gives a more precise error.
10. **How do you know the minimized DFA is correct?** [Isiah] Product-automaton BFS proves it equals the subset DFA (15 pairs, 0 discrepancies), and differential tests agree with `re.fullmatch`.
11. **Formal verification vs testing?** [Isiah] BFS covers every reachable state pair, so it's a proof. Testing compares concrete inputs against an independent reference. It can't prove, but it catches mistakes in how we defined the language.
12. **What is ε-closure?** [Chester] All states reachable using only ε-moves. After `E`, move gives {n1}, closure gives {n1, n2}.
13. **What if the format became `EMP-YYYY-NNNNN`?** [Chester] Change one line (`Repeat(DIGIT, 5)`). Everything regenerates: 28 NFA states, 13 ε, 16 DFA states, 14 rounds, still 0 merges. Tests that pin the old numbers and the hand-written reference table would need updating.
14. **What if lowercase `emp` were allowed?** [Mark] Use `Class(('E','e'))` etc. Σ becomes 17; state counts stay 26 / 15 / 15; |L| becomes 8 × 10⁸.
15. **What if another prefix is added (e.g. `ADM`)?** [Chester] Needs a real code change: the AST has no union of multi-symbol strings yet, only single-symbol classes. We'd add a Union node and its Thompson case.
16. **Why test Unicode look-alikes?** [Isiah] A Cyrillic `Е` or a full-width `０` looks right to a human but is a different symbol. We must reject them. Also `str.isdigit()` would accept Arabic-Indic digits.
17. **Why reject whitespace instead of trimming it?** [Isiah] Space ∉ Σ. The validator decides membership in L exactly as typed. Trimming would be silently changing the input.
18. **How is the GUI separate from the automata logic?** [Chester] Pages only call services and draw the returned results. All decisions happen in `app/core`.
19. **Can the animation and the batch validator disagree?** [Chester] No. Both use `app.core.simulator.Run`, and tests check step-by-step ≡ one-shot for all three models.
20. **How do you keep the docs accurate?** [Rey] Tables are generated from the code (`scripts/gen_docs.py`). `--check` flags stale tables, and `tests/test_docs.py` fails if docs and code disagree.

## Emergency 60-second explanation

> "Our project is the Smart Employee ID Validator. It checks whether a string like EMP-2026-0042 is a valid
> employee ID, but the real point is *how*. We defined the valid IDs as a formal language: an alphabet of 14
> symbols, every ID exactly 13 symbols long, 100 million valid IDs in total. Because the language is finite, it's
> regular, so a finite automaton can recognize it. We wrote it once as a regular expression, and then algorithms
> built every machine: Thompson's construction gives a 26-state ε-NFA, subset construction gives a 15-state DFA,
> and Moore's minimization proves that 15 states is already minimal, because every state needs a different
> number of symbols to reach acceptance. We proved the DFAs equivalent with a product automaton and tested
> everything against Python's regex engine with zero disagreements. Finally, the GUI runs the DFA symbol by symbol,
> so you can watch each transition, see where a bad ID falls into the trap state, and see why an ID is accepted."
