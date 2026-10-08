# 04 — Formal and Empirical Verification

[← 03 Automata Theory](03_automata_theory.md) · [Index](README.md) · Next: [05 Software Architecture →](05_architecture.md)

Slide: **7 — Formal and Empirical Verification**  
Presenter: **Isiah Perito — Tester / QA**

---

## 1. Overview: How Do We Know the System is Correct?

In software engineering, testing usually means writing a few test cases and seeing if they pass. But in Automata Theory, we have access to something much stronger: **mathematical proof of language equivalence**.

Our project verifies correctness through two completely separate, complementary approaches:

```text
                                 CORRECTNESS
                                ┌─────┴─────┐
                                ▼           ▼
                         FORMAL PROOF    EMPIRICAL TESTING
                      (Product BFS)   (Differential Testing)
                                │           │
                  Proves: DFA ≡ MinDFA    Checks: DFA == Human intent
                     Covers: ALL strings      Covers: 61,371+ concrete inputs
```

---

## 2. Part A — Formal / Mathematical Verification (Product Automaton BFS)

### Beginner Explanation
Suppose two people each build a maze based on the same rules. How do you prove both mazes are completely identical without checking an infinite number of paths one by one?

You lock the two people together:
1. They start at the entrance of both mazes at the same time: `(Start A, Start B)`.
2. When you say "go left", they both step left in their own maze. Now they are at `(Room 1A, Room 1B)`.
3. If at any step, Person A is standing in an Exit room while Person B is NOT in an Exit room, you've caught a discrepancy! The mazes are not equivalent.
4. If you explore every possible room combination they can ever reach together, and they **always agree on whether they are in an Exit room**, then the two mazes are mathematically guaranteed to behave identically for *every possible journey*.

That is the **Product Automaton**.

### Technical Explanation
To prove that the subset DFA ($M_1$) and the minimal DFA ($M_2$) accept the exact same language ($L(M_1) = L(M_2)$), we construct their synchronous Cartesian product:

$$M_{\times} = M_1 \times M_2 = (Q_1 \times Q_2, \, \Sigma, \, \delta_{\times}, \, (q_{0,1}, q_{0,2}), \, F_{\times})$$

Where the transition function transitions both automata in lockstep on any symbol $a \in \Sigma$:
$$\delta_{\times}((p, q), a) = (\delta_1(p, a), \, \delta_2(q, a))$$

The algorithm is implemented in `app/core/equivalence.py::dfa_equivalent`:

```text
Algorithm: Product Automaton Equivalence via BFS
1. Queue = [ (start_state_1, start_state_2) ]
2. Visited = { (start_state_1, start_state_2) }
3. While Queue is not empty:
     (p, q) = Queue.popleft()
     If (p in F1) != (q in F2):
         Return NOT EQUIVALENT (with counterexample trace)
     For every symbol a in Σ:
         next_pair = (δ1(p, a), δ2(q, a))
         If next_pair not in Visited:
             Visited.add(next_pair)
             Queue.append(next_pair)
4. Return EQUIVALENT
```

#### What Would Count as a Contradiction?
A contradiction occurs if the search discovers any reachable composite state $(p, q)$ where:
$$(p \in F_1 \land q \notin F_2) \quad \lor \quad (p \notin F_1 \land q \in F_2)$$
This would mean there exists an input string $w$ that leads $M_1$ to an accepting state, but leads $M_2$ to a rejecting state. If this occurs, BFS immediately stops and reconstructs the shortest distinguishing word $w$ (the counterexample).

#### The Result on Our Automata
- **Reachable state pairs explored:** Exactly **15 pairs**
  - $(D_0, q_0)$
  - $(D_1, q_1)$
  - $(D_2, q_2)$
  - $\dots$
  - $(D_{13}, q_{13})$
  - $(D_{\text{trap}}, q_{\text{trap}})$
- **Discrepancies found:** **0**
- **Conclusion:** $L(\text{DFA}_{\text{subset}}) \equiv L(\text{DFA}_{\text{minimal}})$. The Moore minimization preserved the exact language with zero loss or drift.

#### Why BFS Constitutes a Formal Proof Over Infinite Strings
The set of all possible input strings $\Sigma^*$ is infinite. However, the number of reachable composite states in $Q_1 \times Q_2$ is finite (at most $|Q_1| \times |Q_2| = 15 \times 15 = 225$).

Because the state space is finite, exploring all reachable composite states via BFS covers all equivalence classes of $\Sigma^*$. If no reachable state pair disagrees on acceptance, no string in $\Sigma^*$ can ever cause them to disagree. This is a complete, closed-form mathematical proof.

---

## 3. Part B — Empirical / Differential Testing

### Beginner Explanation
Even if our two automata are identical to each other, what if our original math was wrong? What if our regex had a typo and we built two identical machines that both do the wrong thing?

To prevent this, we use **differential testing**: we test our machine against an outside, independent referee that we didn't write: Python's standard `re.fullmatch` engine.

We throw tens of thousands of crazy inputs at both systems and verify they agree on every single one.

### Technical Explanation
In `tests/core/test_equivalence.py`, the independent oracle is:
```python
ORACLE = re.compile(r"^EMP-[0-9]{4}-[0-9]{4}$")
```

#### Why Python's `re.fullmatch` is Used (and Why It's NOT the Core Validator)
1. **Role of Python regex:** It acts strictly as an **external oracle** during testing. It has zero knowledge of our NFA, DFA, or transitions.
2. **Why not use it as the actual validator?**
   - Python's regex is a C-based black box. You give it a string, it gives you `True` or `False`.
   - It cannot explain *which* state it reached, it cannot visualize transitions on an interactive canvas, and it does not demonstrate any student understanding of Thompson's construction or subset construction.
3. **Why `re.fullmatch` instead of `re.search` or `$`?**
   - In Python, `re.match(r"^...$", "EMP-2026-0042\n")` will actually return a match because `$` matches before a trailing newline!
   - `re.fullmatch` requires every byte of the string to match from index 0 to the exact end, matching formal language semantics.

#### Test Battery 1: Exhaustive Testing ($\le 4$ Symbols) — 41,371 Strings
We test every conceivable string of length 0, 1, 2, 3, and 4 over our 14-symbol alphabet $\Sigma$:

$$\sum_{k=0}^{4} |\Sigma|^k = 14^0 + 14^1 + 14^2 + 14^3 + 14^4 = 1 + 14 + 196 + 2{,}744 + 38{,}416 = \mathbf{41{,}371 \text{ strings}}$$

- All 41,371 strings were fed into:
  1. Python `re.fullmatch`
  2. Thompson ε-NFA
  3. Subset DFA
  4. Minimal DFA
  5. Simulation engine (`simulate()`)
- **Result:** **0 disagreements**. Every single string was correctly rejected by all 5 engines (since all valid strings must be length 13).

#### Test Battery 2: Randomized & Neighborhood Testing — 20,000 Strings
Using seeded pseudo-random generation:
1. **Valid strings (30%):** Valid IDs like `EMP-2026-0042`.
2. **Mutated strings (40%):** Valid IDs with 1 to 3 random insertions, deletions, or substitutions.
3. **Random noise (30%):** Completely random strings of varying lengths (0 to 20) drawn from $\Sigma$ and extra corrupting characters.
- **Result:** **20,000 strings tested, 0 disagreements**.

#### Test Battery 3: Transition Mutation Testing — 2,940 Mutants
In `tests/core/test_equivalence.py::test_every_single_transition_mutation_is_detected`:
To verify that our equivalence checker is sensitive enough to catch any subtle bug, we systematically generated **mutant automata**:
- For every state $s \in Q$ (15 states):
  - For every symbol $a \in \Sigma$ (14 symbols):
    - For every possible alternative target state $t' \neq \delta(s, a)$ (14 alternative states):
      $$\text{Total mutants} = 15 \times 14 \times 14 = \mathbf{2{,}940 \text{ mutant DFAs}}$$

**Result:** The equivalence checker caught **all 2,940 mutants**, returning a distinguishing counterexample string for every single one! This proves there is no "slack" or unmonitored transition in our DFA.

#### Test Battery 4: Unicode Look-Alike & Sanitization Testing
We specifically test tricky characters that break naive validation scripts:

| Input | Trap / Edge Case | Expected | Caught By |
|---|---|---|---|
| `EMP-2026-0042\n` | Trailing newline (breaks `$` regexes) | REJECT | Layer 1 (`\n` ∉ Σ) |
| `EMP-2026-000１` | Full-width digit (`１` U+FF11) | REJECT | Layer 1 |
| `EMP-2026-٠٠٠١` | Arabic-Indic digits (passes Python `str.isdigit()`) | REJECT | Layer 1 |
| `EMP-2O26-0001` | Latin capital letter `O` instead of zero `0` | REJECT | Layer 1 (`O` ∉ Σ) |
| `EMP-2026‐0001` | Unicode hyphen (`‐` U+2010 vs ASCII `-` U+002D) | REJECT | Layer 1 |
| `ЕMP-2026-0001` | Cyrillic capital `Е` (U+0415) vs Latin `E` (U+0045) | REJECT | Layer 1 |
| `' EMP-2026-0001'` | Leading whitespace (shows GUI doesn't auto-trim) | REJECT | Layer 1 (space ∉ Σ) |

---

## 4. Part C — Formal Proof vs Automated Testing

If a panel member asks: *"Why do you need both formal verification and differential testing?"*, Isiah Perito should deliver this key distinction:

| Dimension | Formal Verification (Product BFS) | Differential Testing (`re.fullmatch`) |
|---|---|---|
| **What it compares** | DFA A vs DFA B | DFA vs External Python Regex Oracle |
| **Input coverage** | **Infinite** ($\Sigma^*$ — all possible strings) | **Finite** (61,371+ sampled strings) |
| **Nature of check** | Closed-form mathematical proof | Empirical observation |
| **What it proves** | That minimization did not change the language | That our formal language matches real-world regex expectations |
| **Failure mode caught** | Algorithmic bugs in subset construction or minimization | Flaws in the original language specification itself |
| **Can it find counterexamples?** | Yes, BFS finds the shortest counterexample | Yes, outputs the specific failed string |

### Summary Statement for Defense
> "Formal verification proves our machines are mathematically identical to each other across all infinite strings. Differential testing proves that our machines agree with an independent industry-standard oracle on thousands of real-world edge cases. Together, they eliminate both implementation bugs and specification errors."
