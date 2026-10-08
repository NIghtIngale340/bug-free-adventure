# 07 — Slide-by-Slide Presentation Flow & Defense Timeline

[← 06 Validation Flows](06_validation_flows.md) · [Index](README.md) · Next: [08 Live Demo & Roles →](08_live_demo.md)

This document provides the complete spoken presentation script for all 14 slides, followed by a realistic 8–10 minute defense schedule.

---

## Part 1: Slide-by-Slide Script

---

### Slide 1: Title Slide — Smart Employee ID Validator
- **Slide Title:** Smart Employee ID Validator: Algorithmic derivation, formal verification, and interactive simulation of an organization-defined automaton
- **Presenter:** **Ken Ira L. Talingting — Project Leader**
- **Purpose:** Introduce the project, establish its academic foundation, and set the core thesis.
- **What the Audience Should Understand:** This project is not a simple script; it is a full, rigorous translation of formal automata theory into software.
- **What Is Shown:** Project title, course code (CCAUTOMA), subtitle, five pipeline badges (`Language`, `Regex`, `ε-NFA`, `DFA`, `Simulation`), and team member names.
- **What the Presenter Says:**
  > "Good day, esteemed panel and professors. We are here to present our project for CCAUTOMA: the **Smart Employee ID Validator**.
  > 
  > At first glance, validating an employee ID looks like a standard programming exercise. But in this project, we treat it as something much more fundamental: **we demonstrate how a formal language is compiled mathematically, stage by stage, into an executable automaton**, and how that automaton can be verified and made observable in software.
  > 
  > Over the next few minutes, we will walk you through the formal language, the inductive compilation from regular expression to minimal DFA, our mathematical equivalence proofs, and a live demonstration of the system in action.
  > 
  > To begin with the formal definition of our language, I will turn the floor over to our Language Analyst, Mark Anub."
- **What the Presenter Should Emphasize:** "This is not just a validator. It is a formal language turned into an executable automaton, algorithmically."
- **Transition:** Hand off to Mark Anub for Slide 2.
- **Possible Panel Question:** *"Why choose an Employee ID format instead of a programming language grammar?"*
  - **Answer (Ken):** "An Employee ID has fixed structure, character classes, and sequential dependencies. This makes it complex enough to illustrate Thompson's construction, subset construction, and minimization, while remaining concise enough to visualize and formally prove completely within our project scope."

---

### Slide 2: The Employee ID Language
- **Slide Title:** 02 · Problem Definition — The Employee ID Language
- **Presenter:** **Mark Christian T. Anub — Language Analyst & DFA Designer**
- **Purpose:** Formally define the alphabet $\Sigma$, the language $L$, its cardinality, and establish its classification in the Chomsky hierarchy.
- **What the Audience Should Understand:** $L$ is a finite formal language over a 14-symbol alphabet with length 13 and $10^8$ members; therefore, it is regular.
- **What Is Shown:** Structural diagram of `EMP-YYYY-NNNN`, the alphabet $\Sigma$ of 14 symbols, mathematical definition of $L$, $|L| = 10^8$, length = 13.
- **What the Presenter Says:**
  > "Thank you, Ken. Every formal language begins with its alphabet. Our alphabet $\Sigma$ contains exactly **14 symbols**: the three uppercase letters `E`, `M`, and `P`, the hyphen separator `-`, and the ten decimal digits `0` through `9`. It is strictly ASCII.
  > 
  > Our language $L$ is defined as the set of all strings composed of the fixed prefix `EMP-`, followed by a four-digit year, another hyphen, and a four-digit sequence number. Every valid string has an exact length of **13 symbols**.
  > 
  > Because there are exactly 8 independent digit positions, the total cardinality of our language is $|L| = 10^8$, or exactly 100 million valid words. 
  > 
  > Academically, because $L$ is a finite language, it is **provably regular**—every finite language can be represented as a finite union of single-string regular expressions.
  > 
  > Next, our Presentation Lead, James Dotosme, will introduce our automated compilation pipeline."
- **What the Presenter Should Emphasize:** $|\Sigma| = 14$, length = 13, and finite implies regular.
- **Transition:** Hand off to James Dotosme for Slide 3.
- **Possible Panel Question:** *"Does regular imply finite?"*
  - **Answer (Mark):** "No, sir. Finite implies regular, but regular languages can be infinite, such as $(a)^*$. Our language happens to be both finite and regular."

---

### Slide 3: The Automata Pipeline
- **Slide Title:** 03 · Construction — The Automata Pipeline
- **Presenter:** **James Paul B. Dotosme — Presentation Lead**
- **Purpose:** Present the high-level compilation roadmap from regex to simulation.
- **What the Audience Should Understand:** The transitions are not hand-drawn; they are derived automatically through classic algorithms.
- **What Is Shown:** Horizontal 5-stage pipeline diagram: `Regex AST (EMP-D⁴-D⁴)` $\to$ `Thompson ε-NFA (26)` $\to$ `Subset DFA (15)` $\to$ `Minimal DFA (15)` $\to$ `Verification & Simulator`.
- **What the Presenter Says:**
  > "Thank you, Mark. Rather than manually designing a state machine, our system implements an end-to-end automata compiler.
  > 
  > As shown on this roadmap, we begin with the formal Regular Expression AST. We pass that tree to **Thompson's Construction**, which outputs an $\varepsilon$-NFA of 26 states.
  > 
  > We then feed that NFA into the **Rabin–Scott Subset Construction**, which converts nondeterminism into a deterministic DFA of 15 states, including an explicit trap state.
  > 
  > Next, we execute **Moore's Partition Refinement** to minimize the DFA. We formally verify equivalence using a product automaton, and finally load the resulting machine into our simulation engine.
  > 
  > Chester Lauzon, our programmer and automata optimizer, will now explain how the $\varepsilon$-NFA is constructed."
- **What the Presenter Should Emphasize:** Each stage's output is the input to the next stage.
- **Transition:** Hand off to Chester Lauzon for Slide 4.

---

### Slide 4: Thompson’s ε-NFA
- **Slide Title:** 04 · Stage 2 — Thompson’s ε-NFA
- **Presenter:** **Chester Josh C. Lauzon — Programmer & Automata Optimizer**
- **Purpose:** Explain Thompson's inductive construction, the state count (26), $\varepsilon$-transitions (12), and the digit class atom.
- **What the Audience Should Understand:** Thompson's construction builds inductive fragments; character-class consolidation prevents unnecessary state explosion.
- **What Is Shown:** Regex fragment breakdown `EMP-D⁴-D⁴`, 26 states ($n_0 \dots n_{25}$), 12 $\varepsilon$-transitions, diagram excerpt of concatenation with $\varepsilon$-edges.
- **What the Presenter Says:**
  > "To convert our regex AST into an automaton, we implement Thompson's Construction. Thompson's algorithm compiles each basic regex atom into a two-state machine and glues them together using $\varepsilon$-transitions.
  > 
  > Our ID pattern consists of 13 sequential atomic fragments: 3 prefix letters, 2 hyphens, and 8 digits. With 2 states per atom, this yields exactly **26 states**, from start state $n_0$ to accepting state $n_{25}$.
  > 
  > Concatenating these 13 fragments requires exactly $13 - 1 = \mathbf{12 \varepsilon\text{-transitions}}$.
  > 
  > A key engineering decision we made was the **character-class Thompson atom**. Standard textbook Thompson construction creates branching unions for alternatives, which would blow up each digit into over 20 states and balloon our NFA to nearly 200 states. Instead, we represent $D = (0 \cup \dots \cup 9)$ as an atomic fragment with 10 parallel transitions. This preserves exact language semantics while keeping the automaton transparent and mathematically clean."
- **What the Presenter Should Emphasize:** 26 states, 12 $\varepsilon$-transitions, and character-class atom optimization.
- **Transition:** Proceed to Slide 5 (Chester continues).

---

### Slide 5: Subset Construction
- **Slide Title:** 05 · Stage 3 — Subset Construction
- **Presenter:** **Chester Josh C. Lauzon — Programmer**
- **Purpose:** Explain Rabin–Scott subset construction, elimination of $\varepsilon$-moves, the 15-state count, and total $\delta$.
- **What the Audience Should Understand:** Subsets of NFA states become single DFA states; an explicit trap state guarantees a total transition function.
- **What Is Shown:** Algorithm summary ($\varepsilon\text{-closure}(\text{move}(S, a))$), 15 states (14 live $D_0 \dots D_{13}$ + 1 dead $D_{\text{trap}}$), transition table summary ($15 \times 14 = 210$ transitions).
- **What the Presenter Says:**
  > "To make the automaton executable without backtracking, we convert the NFA into a DFA using Rabin–Scott Subset Construction.
  > 
  > Starting with the $\varepsilon$-closure of $n_0$, for each subset of NFA states and each symbol in $\Sigma$, we compute $\text{move}(S, a)$ and take its $\varepsilon$-closure. Each unique subset becomes a single state in our new DFA.
  > 
  > This produces **14 live states**, $D_0$ through $D_{13}$, corresponding to having matched 0 through 13 valid characters.
  > 
  > In addition, whenever an input symbol is invalid for a given state, the transition leads to the empty set. We map this empty set to an explicit dead state, **$D_{\text{trap}}$**.
  > 
  > This gives us a **total transition function**: all 15 states have a defined transition for all 14 alphabet symbols, resulting in exactly $15 \times 14 = 210$ table entries. The machine never hits an undefined condition at runtime."
- **What the Presenter Should Emphasize:** 14 live states + 1 trap state = 15 total states; total transition function.
- **Transition:** Proceed to Slide 6 (Chester continues).

---

### Slide 6: Minimization and the No-Merge Proof
- **Slide Title:** 06 · Stage 4 — Minimization and the No-Merge Proof
- **Presenter:** **Chester Josh C. Lauzon — Automata Optimizer**
- **Purpose:** Explain Moore partition refinement, the 13 refinement rounds, why zero states merge, and the mathematical proof of minimality.
- **What the Audience Should Understand:** Zero merges is not a failure; it is formal verification that our subset DFA was already minimal.
- **What Is Shown:** Distance strip showing shortest accepting distance from each state ($D_0 \to 13, D_1 \to 12, \dots, D_{13} \to 0, D_{\text{trap}} \to \infty$), Moore partition sequence $P_0 \to \dots \to P_{13}$, result: 15 in $\to$ 15 out.
- **What the Presenter Says:**
  > "With a complete DFA in hand, we apply **Moore's Partition Refinement** to minimize it.
  > 
  > We start with partition $P_0$, which splits accepting states from non-accepting states. We then iteratively refine blocks whenever states transition to different blocks on any symbol. It takes **13 rounds** to stabilize, and at the end, **zero states merge**: 15 states enter, and 15 states leave.
  > 
  > Why did zero states merge? Look at the shortest accepting distance for each state. From state $D_i$, the shortest string that reaches acceptance has length exactly $13 - i$. $D_0$ requires 13 symbols, $D_{12}$ requires 1, $D_{13}$ requires 0, and the trap state can never accept—its distance is infinity.
  > 
  > Because every single state has a strictly unique distance to acceptance, every pair of states is distinguishable. By the Myhill–Nerode theorem, this proves that our DFA is **already minimal**. Zero merges is not an optimization failure—it is mathematical confirmation of minimality.
  > 
  > Now, our QA Lead, Isiah Perito, will explain how we verified this automaton."
- **What the Presenter Should Emphasize:** $d(D_i, F) = 13 - i$ are all distinct $\implies$ pairwise distinguishable $\implies$ already minimal.
- **Transition:** Hand off to Isiah Perito for Slide 7.

---

### Slide 7: Formal and Empirical Verification
- **Slide Title:** 07 · Stage 5 — Formal and Empirical Verification
- **Presenter:** **Isiah Thomas A. Perito — Tester / QA**
- **Purpose:** Present the dual verification strategy: Product Automaton BFS (formal proof) vs Differential Testing (empirical testing).
- **What the Audience Should Understand:** We didn't just run test cases; we formally proved language equivalence and differentially tested edge cases.
- **What Is Shown:** Two columns: Left (Formal: Product BFS $DFA_{\text{subset}} \times DFA_{\text{minimal}}$, 15 state-pairs checked, 0 discrepancies); Right (Empirical: vs Python `re.fullmatch`, 41,371 exhaustive strings $\le 4$, 20,000 randomized/mutated strings, 0 disagreements).
- **What the Presenter Says:**
  > "Thank you, Chester. To guarantee complete correctness, we verified our automaton in two independent ways.
  > 
  > On the left is our **formal mathematical proof**. We construct the Product Automaton of the subset DFA and the minimal DFA, traversing reachable composite state pairs via Breadth-First Search. If any reachable pair contained one accepting and one non-accepting state, the languages would differ. We explored all 15 reachable state pairs and found **zero discrepancies**, proving that both machines accept the identical language across all possible strings in $\Sigma^*$.
  > 
  > On the right is **empirical differential testing**. We tested our automaton against Python's standard `re.fullmatch` engine on **41,371 exhaustive strings** of length 4 or less, plus **20,000 randomized, mutated, and Unicode look-alike strings**. Across all 61,371 test cases, we found **zero disagreements**.
  > 
  > Chester will now show how this theory is structured into software."
- **What the Presenter Should Emphasize:** Formal proof covers infinite strings; differential testing checks against an outside oracle.
- **Transition:** Hand off to Chester Lauzon for Slide 8.

---

### Slide 8: Software Architecture
- **Slide Title:** 08 · Implementation — Software Architecture
- **Presenter:** **Chester Josh C. Lauzon — Programmer**
- **Purpose:** Explain the three-tier software architecture and the separation between the GUI and automata engine.
- **What the Audience Should Understand:** The GUI contains zero automata logic; `app.core.simulator.Run` is the single source of truth.
- **What Is Shown:** Architectural diagram: Presentation (PySide6) $\to$ Service (`SimulationService`, `ValidationService`) $\to$ Automata Core (`pipeline.py`, `simulator.py`, `minimizer.py`, `nfa.py`, `dfa.py`), plus 3 validation layers.
- **What the Presenter Says:**
  > "Our software architecture is organized into three decoupled layers.
  > 
  > At the bottom is the **Automata Core**, written in pure Python with zero UI dependencies. In the middle is the **Service Layer**, which coordinates sessions and packages results. At the top is the **Presentation Layer**, built using PySide6.
  > 
  > A cardinal rule of our design is that **the GUI contains zero automata logic**. The pages only request simulations and render the structured results returned to them.
  > 
  > Furthermore, a single execution engine—`app.core.simulator.Run`—powers interactive UI stepping, batch validation, and automated pytest execution. This guarantees that the visual simulator and batch validator can never diverge.
  > 
  > James will now walk us through the user interface."
- **What the Presenter Should Emphasize:** Single source of truth (`Run`); GUI has 0 automata logic.
- **Transition:** Hand off to James Dotosme for Slide 9.

---

### Slide 9: The Educational GUI
- **Slide Title:** 09 · Interface — The Educational GUI
- **Presenter:** **James Paul B. Dotosme — Presentation Lead**
- **Purpose:** Introduce the GUI layout and its pedagogical visualization features.
- **What the Audience Should Understand:** The GUI makes automata theory observable by rendering tape position, regex segments, active transitions, and visited states.
- **What Is Shown:** Annotated screenshot of the Simulate page: 1. Interactive Tape, 2. Regex segment indicators, 3. Active transition arrow, 4. Visited state highlights, 5. Stepping/playback controls, keyboard shortcuts.
- **What the Presenter Says:**
  > "Thank you, Chester. The GUI was designed specifically as an educational tool to make automata theory visible.
  > 
  > At the top (1), the **Interactive Tape** displays each symbol and highlights the active head. Below it (2), colored bars map each symbol to its corresponding regex segment: prefix, separator, year, or sequence.
  > 
  > On the canvas (3), the amber arrow illuminates the active transition $\delta(q, a)$ being evaluated. Visited states (4) remain highlighted to show the execution path. And at the bottom (5), full controls allow stepping forward, backward, or playing at adjustable speeds, with full keyboard navigation.
  > 
  > Let's look at what happens when a valid ID is executed."
- **What the Presenter Should Emphasize:** Built to make automata theory observable.
- **Transition:** Proceed to Slide 10 (James continues).

---

### Slide 10: Demo — An Accepted ID
- **Slide Title:** 10 · Live Demonstration — Demo: An Accepted ID
- **Presenter:** **James Paul B. Dotosme — Presentation Lead**
- **Purpose:** Demonstrate the execution trace of a valid input.
- **What the Audience Should Understand:** The valid ID traces a 13-step path ending at accepting state $q_{13}$.
- **What Is Shown:** Input `EMP-2026-0042`, step-by-step transition path from $q_0$ to $q_{13}$, verdict: FINAL STATE $q_{13}$, 13/13 symbols accepted.
- **What the Presenter Says:**
  > "Here we evaluate the canonical valid input: `EMP-2026-0042`.
  > 
  > Starting at state $q_0$, the machine matches `E`, `M`, and `P`, reaching state $q_3$. It consumes the first hyphen to reach $q_4$, reads the four year digits `2`, `0`, `2`, `6` to reach $q_8$, consumes the second hyphen to reach $q_9$, and reads the four sequence digits `0`, `0`, `4`, `2`.
  > 
  > At the end of the 13th symbol, the machine rests in state **$q_{13}$**. Because $q_{13}$ belongs to the accepting set $F$, the banner displays a green **ACCEPTED** verdict.
  > 
  > Now, Mark and Chester will explain what happens when an input is invalid."
- **What the Presenter Should Emphasize:** 13 symbols, 13 transitions, terminal state $q_{13} \in F$.
- **Transition:** Hand off to Mark Anub and Chester Lauzon for Slide 11.

---

### Slide 11: Two Rejection Modes
- **Slide Title:** 11 · Invalid Inputs — Two Rejection Modes
- **Presenter:** **Mark Christian T. Anub** (Case A & B theory) & **Chester Josh C. Lauzon** (implementation)
- **Purpose:** Differentiate between structural rejection (inside the DFA via trap state) and alphabet rejection (before the DFA via Layer 1).
- **What the Audience Should Understand:** Rejection is not uniform: strings with bad symbols fail before the DFA; strings with bad structure fail inside the DFA via $q_{\text{trap}}$.
- **What Is Shown:** Case A (Structural Rejection: `EMP2026-0001`, `'2' \in \Sigma`, reaches $q_{\text{trap}}$); Case B (Alphabet Rejection: `EMP-2026-12A4`, `'A' \notin \Sigma`, caught by pre-filter).
- **What the Presenter Says:**
  > **Mark:** "Not every invalid input fails for the same reason. In Case A, `EMP2026-0001`, every single character is a legitimate member of our alphabet $\Sigma$. The flaw is structural: after `EMP`, the language demands a hyphen, but reads the digit `2`.
  > 
  > In Case B, `EMP-2026-12A4`, the character `'A'` is simply not in $\Sigma$. That string is not even a valid word over our alphabet."
  > 
  > **Chester:** "In our implementation, these follow two distinct paths. In Case A, the DFA runs normally from $q_0$ to $q_3$. At $q_3$, symbol `'2'` has no forward transition, so $\delta(q_3, '2')$ transitions into **$q_{\text{trap}}$**. The GUI draws a red dashed line into the trap state.
  > 
  > In Case B, our **Layer 1 Alphabet Filter** catches `'A'` at position 11 *before the DFA runs at all*. This preserves the formal mathematical integrity of $\delta$, because $\delta$ is only defined over $\Sigma$."
- **What the Presenter Should Emphasize:** Structural = inside DFA ($q_{\text{trap}}$); Alphabet = outside DFA (Layer 1 pre-filter).
- **Transition:** Hand off to Isiah Perito for Slide 12.

---

### Slide 12: Test Suite and Edge Cases
- **Slide Title:** 12 · Testing — Test Suite and Edge Cases
- **Presenter:** **Isiah Thomas A. Perito — Tester / QA**
- **Purpose:** Present the test suite metrics, edge case categories, and model agreement.
- **What the Audience Should Understand:** The test suite covers 28 predefined cases and 250+ automated tests across boundary years, hyphens, and whitespace.
- **What Is Shown:** Test suite metrics: 28 predefined cases (10 valid, 18 invalid), 250+ automated tests (unit, integration, offscreen GUI), edge cases list.
- **What the Presenter Says:**
  > "Thank you, Mark and Chester. To ensure robust operation, we maintain a predefined suite of **28 test cases**: 10 valid and 18 invalid. On our Tests page, all 28 pass, and all three models—the ε-NFA, subset DFA, and minimal DFA—agree 100% on all 28 inputs.
  > 
  > Supporting this are **over 250 automated pytest cases** covering unit algorithms, pipeline integration, and offscreen GUI rendering.
  > 
  > Our edge cases test strict boundaries: boundary years like 2000 and 2099, missing or double hyphens, underscores, lowercase prefixes, truncated inputs, empty strings, and untrimmed whitespace.
  > 
  > Rey and Chester will now highlight our key engineering decisions."
- **What the Presenter Should Emphasize:** Testing edge cases and boundary conditions; all three automata models agree.
- **Transition:** Hand off to Rey Ayson and Chester Lauzon for Slide 13.

---

### Slide 13: Engineering Decisions
- **Slide Title:** 13 · Highlights — Engineering Decisions
- **Presenter:** **Chester Josh C. Lauzon** (Cards 1–2) & **Rey Noel C. Ayson — Documentation** (Cards 3–4)
- **Purpose:** Highlight best practices in software engineering, reproducible documentation, and accessibility.
- **What the Audience Should Understand:** The system incorporates high-quality engineering: unified simulation engine, digit atom, automated doc sync, and accessibility.
- **What Is Shown:** 4 highlight cards: 1. Unified simulation engine (`Run`), 2. Character-class Thompson atom, 3. Reproducible documentation, 4. Accessibility and motion control.
- **What the Presenter Says:**
  > **Chester:** "Two engineering decisions shaped the codebase. First, the unified simulation engine: `app.core.simulator.Run` drives interactive GUI stepping, batch runs, and tests, eliminating duplicated logic. Second, the character-class Thompson atom: consolidating digit transitions prevented exponential state bloat while preserving exact semantics."
  > 
  > **Rey:** "On the documentation side, our tables and diagrams are not typed by hand. Our documentation artifacts are **regenerated automatically from the implementation**, with automated tests verifying that documentation never goes stale. Finally, for accessibility, the simulator features full keyboard navigation and supports reduced-motion environments."
- **What the Presenter Should Emphasize:** Derivation over manual typing applies to both the automata and the documentation.
- **Transition:** Hand off to Ken Talingting for Slide 14.

---

### Slide 14: Conclusion & Summary
- **Slide Title:** 14 · Conclusion — Summary & Q&A
- **Presenter:** **Ken Ira L. Talingting — Project Leader**
- **Purpose:** Summarize the core accomplishments, re-iterate team contributions, and open the floor for defense Q&A.
- **What the Audience Should Understand:** The project successfully demonstrates end-to-end derivation, minimality, verification, and interactive simulation.
- **What Is Shown:** Summary roadmap, 3 core pillars: 15-state DFA is minimal, Formal equivalence verified, Working educational GUI.
- **What the Presenter Says:**
  > "To conclude: our project successfully demonstrates the complete translation of formal language theory into reliable software.
  > 
  > Starting from a single regular expression, we algorithmically compiled an $\varepsilon$-NFA of 26 states, derived a 15-state DFA, proved via Moore's algorithm that the 15-state DFA is minimal, formally verified equivalence with a product automaton, and packaged the entire machine into an interactive educational GUI.
  > 
  > Each member of our team owned an integral role: Mark on language analysis, James on presentation, Chester on programming and optimization, Isiah on testing and QA, Rey on documentation, and myself on project coordination.
  > 
  > Thank you for your time, and we are now ready for your questions and our live demonstration."
- **What the Presenter Should Emphasize:** Theoretical rigor backed by working software.
- **Transition:** Move immediately to the Live Demonstration (or Q&A as directed by panel).

---

## Part 2: Minute-by-Minute Defense Timeline (8–10 Minutes)

| Time | Slide / Activity | Presenter | Spoken Focus | Screen / Visual State |
|---|---|---|---|---|
| **0:00–0:45** (45s) | Slide 1: Title | Ken Talingting | Project overview, core thesis, pipeline intro | Slide 1 displayed |
| **0:45–1:45** (60s) | Slide 2: Formal Language | Mark Anub | Alphabet $\Sigma$, language $L$, $|L|=10^8$, finite $\implies$ regular | Slide 2 displayed |
| **1:45–2:30** (45s) | Slide 3: Pipeline | James Dotosme | High-level compiler flow from regex AST to simulation | Slide 3 displayed |
| **2:30–3:30** (60s) | Slide 4: Thompson ε-NFA | Chester Lauzon | 26 states, 12 $\varepsilon$-edges, digit class atom | Slide 4 displayed |
| **3:30–4:30** (60s) | Slide 5: Subset Construction | Chester Lauzon | Subset algorithm, 14 live + 1 trap = 15 states, total $\delta$ | Slide 5 displayed |
| **4:30–5:45** (75s) | Slide 6: Minimization & Proof | Chester Lauzon | Moore algorithm, 13 rounds, 0 merges, distance proof | Slide 6 displayed |
| **5:45–6:45** (60s) | Slide 7: Verification | Isiah Perito | Product BFS proof vs differential testing against `re.fullmatch` | Slide 7 displayed |
| **6:45–7:30** (45s) | Slide 8: Architecture | Chester Lauzon | Three tiers, GUI has 0 automata logic, single `Run` engine | Slide 8 displayed |
| **7:30–8:15** (45s) | Slide 9: Interface | James Dotosme | UI features: tape, RE segments, canvas, controls | Slide 9 displayed |
| **8:15–9:30** (75s) | **LIVE DEMO** (Slides 10–11) | James, Mark, Chester | Live run of `EMP-2026-0042`, `EMP2026-0001`, `EMP-2026-12A4` | **Switch to live PySide6 App** |
| **9:30–10:00** (30s) | Slide 12–14: Conclusion | Isiah, Rey, Ken | Test suite summary, engineering highlights, wrap-up | Return to slides (12 $\to$ 14) |
| **10:00+** | **DEFENSE Q&A** | All Team Members | Defend technical decisions and answer panel questions | App or slides as reference |
