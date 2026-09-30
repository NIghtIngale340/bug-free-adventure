# ORAL DEFENSE PLAYBOOK: LIVE DEMO SCRIPT & Q&A QUESTION BANK

**Course:** CCAUTOMA — Formal Languages & Automata Theory  
**Team:** Ken (Backend/Theory), Chester (Frontend/GUI), Integrator (System/QA)  
**Window:** 8–10 minutes (presentation ≈ 4 min · live demo ≈ 4 min · Q&A ≈ 2 min)

Every statement below is backed by code or a test in this repository. If you change the code, re-run
`python -m pytest` and `python scripts/gen_docs.py --check` before rehearsing.

## Before you present

- Start with `python -m app.main` from anywhere; window opens on **Simulate**.
- Type inputs and press **Enter** (or **Load**). Loading never starts the run — you decide when to **Step**, **Play** or **Run all**.
- Shortcuts: **Space** play/pause · **→** step · **←** previous step · **Ctrl+R** reset.
- Pre-run once: Tests tab → all 28 pass; Theory → Equivalence → *Run exhaustive check* (takes about a second).

## 1. The 4-minute live demonstration

### Minute 1 — Theory overview (Ken) · Theory tab
Show **Language**, then **Regular expression**, then click through **ε-NFA → Subset construction → Minimization**.

> "Our language is `EMP-YYYY-NNNN` over an alphabet of 14 symbols. Its regular expression is `EMP-D⁴-D⁴` with `D` the union of the ten digits.
> We did not type an automaton. We built an **ε-NFA from the RE with Thompson's construction** — 26 states and 12 ε-edges. **Subset construction** turned it into a DFA with 14 live states plus an explicit dead state. **Partition refinement** minimized it: it takes 13 rounds and merges nothing, because every state needs a different number of further symbols to reach acceptance. That minimal DFA is what the simulator runs."

### Minute 2 — Valid ID, step by step (Chester) · Simulate tab
Type `EMP-2026-0042`, press Enter. Press **Step** four times, then **Run all**.

> "The tape shows the input; the automaton sits in its start state `q0`. Each step consumes one symbol: `E` takes `q0` to `q1`, `M` to `q2`, `P` to `q3`, `-` to `q4`. The coloured bars under the tape show which part of the regular expression each symbol matches. The amber edge is the transition just taken, tinted states were visited, unvisited states stay plain. Hover any state or edge and the strip under the diagram explains it — e.g. `q3` expects `-` and needs at least 10 more symbols. After 13 symbols we are in `q13`, which is in F: **ACCEPTED**."

Optional (10 s): switch **Model** to *ε-NFA* and Step once: "after `E` the NFA is in `{n1, n2}` — that is the ε-closure at work."

### Minute 3 — Two kinds of rejection (Chester + Ken) · Simulate tab
1. Type `EMP2026-0001`, Step to position 3.
   > "All symbols are in Σ, so the automaton runs. In `q3` it expects `-` but reads `2`. There is no valid transition, so it enters the dead state `q_trap` — shown by the dashed red edge — and stays there. **REJECTED at position 3.**"
2. Type `EMP-2026-12A4`.
   > "`A` is not in Σ. Layer 1 checks the whole string against the alphabet *before* the automaton runs, so no state is visited: this is not a string over Σ at all. **REJECTED: 'A' at position 11.**"

### Minute 4 — Verification and architecture (Integrator) · Tests tab, then Theory → Equivalence
Tests tab:

> "28 categorized cases, 28 pass, and the ε-NFA, the pre-minimization DFA and the minimal DFA agree on all 28."

Theory → Equivalence → **Run exhaustive check**:

> "The minimal DFA equals the subset DFA by an exact product-automaton check over 15 state pairs. We also ran every word up to length 4 — 41,371 words — through the NFA and both DFAs against a Python regex oracle: 0 disagreements. The GUI contains no automata logic; it renders results from the services."

## 2. Q&A bank

### Ken (theory)

**Q1. Why is this language regular?**  
It is finite (10⁸ words, each of length 13). Every finite language is regular; concretely a DFA that counts 0…13 symbols recognizes it, so no stack or unbounded counter is needed.

**Q2. How did you convert the NFA to a DFA?**  
Rabin–Scott subset construction (`app/core/nfa.py::subset_construction`). The start subset is the ε-closure of `n0`. For each subset and symbol we compute `move` then ε-closure; each new subset is a DFA state and the empty subset is the dead state. The Theory → *Subset construction* tab shows every step, e.g. after `E`: `move = {n1}`, closure `{n1, n2}`.

**Q3. Is your NFA really nondeterministic?**  
It has ε-transitions (12), so it is an ε-NFA. For this particular language the ε-closures are deterministic, so the subset DFA is a chain — a property of the language, not a shortcut in the code. The code handles real nondeterminism too (tested with an NFA that has two `a`-moves).

**Q4. How did you minimize, and were any states merged?**  
Partition refinement (Moore): start from {F, Q∖F}, split blocks whose members reach different blocks on some symbol, repeat. It stabilises after 13 rounds with 15 singleton blocks, so nothing merges. Each round isolates one more state, mirroring the fact that from `qᵢ` the shortest accepted word has length 13−i. Minimization is also tested on a redundant DFA where two pairs of states really merge.

**Q5. Why couldn't the DFA be reduced further?**  
From `qᵢ` you need exactly `13−i` more symbols to accept, so no two live states are equivalent; `q13` is the only accepting state; `q_trap` can never accept. The Minimization tab computes these numbers from the automaton.

**Q6. Is δ total? Where is the trap state?**  
Yes. Every (state, symbol) pair of Σ has an explicit next state; undefined moves go to `q_trap`, which loops on every symbol (shown in every empty table cell).

**Q7. What happens when the user types a symbol that is not in Σ?**  
Layer 1 checks the whole string against Σ first. If any symbol is outside Σ the input is not a string over Σ, so the automaton does not run: REJECTED, with every offending symbol and position listed. δ is not defined for such symbols — `DFA.step` refuses them.

**Q8. What about the empty string?**  
ε is not in L because `q0 ∉ F`. The application reports "Please enter an Employee ID" and does not simulate.

### Chester (GUI)

**Q9. Where is the validation logic in the GUI?**  
Nowhere. The widgets call `SimulationService` and render `SimulationResult` / `TransitionStep`. The diagram is drawn from the automaton objects themselves (`app/core/present.py` builds the graph).

**Q10. Can the GUI and the validator disagree?**  
No: one engine (`app.core.simulator.Run`) powers both the animated session and the one-shot result, and tests check step-by-step ≡ one-shot for all three models over the whole suite. The GUI also never trims input, so `"EMP-2026-0001 "` (trailing space) is rejected.

### Integrator (QA / architecture)

**Q11. How do you know the minimized DFA accepts exactly the same language?**  
Exact proof: BFS over the product automaton finds no reachable pair where exactly one side accepts (15 pairs explored). We verified the check itself by mutation — flipping any one transition yields a counterexample. In addition: exhaustive comparison of all words ≤ 4, neighbours of valid IDs, and 20,000 random words including Unicode look-alikes against a regex oracle.

**Q12. Why not just use Python's `re`?**  
`re` is a black box. The goal is to expose Σ, Q, δ, q₀, F and the state-by-state run, and to derive each machine from the previous one. We use `re.fullmatch` only as an independent oracle in tests.

**Q13. Why is the RE written as `EMP-D⁴-D⁴` and not `[0-9]{4}`?**  
The course's regular expressions use union, concatenation and repetition. `D` is the union of ten digits; `{4}` is repetition. The PCRE form is kept as a test oracle only (and used with `fullmatch`, because `$` would accept a trailing newline).

**Q14. Why is the digit class one atom in the Thompson NFA?**  
A textbook union `(0∪…∪9)` needs ten branches per digit (~170 states). We collapse each digit class into one atom with ten parallel edges — the standard character-class shortcut — which keeps the NFA at 26 states without changing the language.
