# 08 — Live Demonstration Procedure & Team Responsibilities

[← 07 Presentation Flow](07_presentation_flow.md) · [Index](README.md) · Next: [09 Q&A Bank →](09_qa_bank.md)

This document provides the complete live demo protocol, fail-safe recovery procedures, and the team member duty roster.

---

## Part 1: Live Demonstration Setup & Environment Checklist

### 10 Minutes Before the Defense:
1. **Launch the application:**
   ```bash
   python -m app.main
   ```
2. **Pre-warm test caches:**
   - Navigate to the **Tests** page $\to$ click **Run All Tests** (verifies 28/28 passes).
   - Navigate to **Theory** $\to$ **Equivalence** $\to$ click **Run Equivalence Check** (ensures graph is cached).
3. **Set up the Simulate Page:**
   - Return to the **Simulate** page.
   - Ensure the input box is cleared.
   - Adjust animation speed slider to middle (approx. 500ms per step).
4. **Display Configuration:**
   - Keep the presentation slides on one half of the screen (or primary display) and the PySide6 app on the other (or ready via `Alt+Tab`).
   - Have the terminal running in the background with `pytest` ready to execute if requested.

---

## Part 2: Step-by-Step Live Demo Scripts

---

### Demo 1: Valid ID Acceptance (`EMP-2026-0042`)
- **Presenter:** **James Paul B. Dotosme**
- **Goal:** Show successful deterministic recognition through all 13 states to $q_{13}$.

| Step | Action | Spoken Explanation | Expected UI Result |
|---|---|---|---|
| **1** | Type `EMP-2026-0042` into the input field and press **Enter** (or click **Load**). | "We load a valid ID: `EMP-2026-0042`. Notice the tape at the top shows all 13 characters, and the colored bars below map them to our regex segments." | Input tape displays string; cursor rests at position 0 (`'E'`). Current state highlights at $q_0$. |
| **2** | Press **Space** (or click **Play**), or press the **Right Arrow ($\to$)** to step manually. | "As we step through, observe the amber arrow showing the active transition $\delta(q, a)$. The tape advances, and visited states stay tinted. We pass through `EMP`, the hyphen, the four year digits, the second hyphen, and the four sequence digits." | State nodes illuminate in sequence: $q_0 \to q_1 \to \dots \to q_{13}$. Tape pointer moves in sync. |
| **3** | Allow the simulation to reach the end of the input. | "On consuming the 13th symbol, the automaton halts in state $q_{13}$. Because $q_{13}$ is in $F$, the system produces an ACCEPTED verdict." | Emerald green **ACCEPTED** banner appears; double border around $q_{13}$ glows; history log shows 13 transitions. |

- **Technical Meaning:** Demonstrates that the minimal DFA correctly accepts words in $L$, executing in linear time $O(|w| = 13)$ with zero backtracking.
- **Fail-Safe Recovery:** If animation stutters, press **Ctrl+R** (reset), click **Run All** (instant validation), which bypasses GUI timers and instantly renders the final state.

---

### Demo 2: Structural Rejection / Trap State (`EMP2026-0001`)
- **Presenter:** **Mark Christian T. Anub & Chester Josh C. Lauzon**
- **Goal:** Show that an ID made of valid alphabet symbols but invalid grammar transitions to $q_{\text{trap}}$.

| Step | Action | Spoken Explanation | Expected UI Result |
|---|---|---|---|
| **1** | Type `EMP2026-0001` and press **Enter**. | "Now we test a structural error: `EMP2026-0001`. The first hyphen is missing, though every symbol belongs to our alphabet $\Sigma$." | Tape loads string. Cursor at index 0. |
| **2** | Press **Right Arrow ($\to$)** 3 times to step to state $q_3$. | "The machine reads `E`, `M`, and `P` normally, reaching state $q_3$." | Canvas highlights path $q_0 \to q_1 \to q_2 \to q_3$. Tape pointer at index 3 (`'2'`). |
| **3** | Press **Right Arrow ($\to$)** a 4th time. | "At state $q_3$, the machine expects a hyphen `-`. But the next symbol is `'2'`. In our DFA table, $\delta(q_3, '2') = q_{\text{trap}}$." | A **dashed red arrow** darts from $q_3$ directly into $q_{\text{trap}}$. The trap state turns crimson. |
| **4** | Point to the verdict banner. | "Because $q_{\text{trap}}$ can never accept, the engine halts immediately. The banner pinpoints the exact error: expected `-` at position 3, but received `'2'`." | Red **REJECTED** banner displays: `REJECTED_NO_TRANSITION: At position 3, expected '-' from state q3`. |

- **Technical Meaning:** Demonstrates the total transition function $\delta$ and shows that dead state isolation provides precise syntax error localization.
- **Fail-Safe Recovery:** If user accidentally types something else, click the input box, paste `EMP2026-0001`, and click **Run All**.

---

### Demo 3: Alphabet Rejection (`EMP-2026-12A4`)
- **Presenter:** **Mark Christian T. Anub**
- **Goal:** Show that an input containing symbols outside $\Sigma$ is caught by Layer 1 before the DFA executes.

| Step | Action | Spoken Explanation | Expected UI Result |
|---|---|---|---|
| **1** | Type `EMP-2026-12A4` and press **Enter** (or click **Run All**). | "Now we enter `EMP-2026-12A4`. Notice that the 12th character is the letter `'A'`, which is not in our alphabet $\Sigma$." | Instant red **REJECTED** banner appears without animation. |
| **2** | Point to the tape and diagram canvas. | "Notice that the state diagram did NOT transition to any state. Why? Because character `'A'` is outside $\Sigma$. Our Layer 1 pre-filter intercepted it before the DFA ran, identifying symbol `'A'` at position 11." | Tape highlights `'A'` in red. Canvas states remain unvisited. Error banner reads: `REJECTED_INVALID_SYMBOL: 'A' at position 11 is not in Σ`. |

- **Technical Meaning:** Demonstrates that the mathematical domain of $\delta$ is strictly preserved ($\delta: Q \times \Sigma \to Q$), preventing undefined behavior.

---

### Demo 4: Theory & Derivation Inspection
- **Presenter:** **Chester Josh C. Lauzon**
- **Goal:** Show that the automata models, transition tables, and minimization rounds are generated by code.

| Step | Action | Spoken Explanation | Expected UI Result |
|---|---|---|---|
| **1** | Click **Theory** in the left navigation sidebar. | "On our Theory page, all tables and diagrams are derived directly from our automata core algorithms." | Theory dashboard loads. |
| **2** | Click the **ε-NFA** tab. | "Here is the Thompson ε-NFA showing all 26 states and 12 ε-transitions." | Transition table and state diagram displayed. |
| **3** | Click the **Subset Construction** tab. | "Here is the Rabin–Scott subset construction table showing the transformation from sets of NFA states to our 15 DFA states." | Table showing subsets and move operations. |
| **4** | Click the **Minimization** tab. | "Here is Moore's partition refinement showing all 13 rounds, proving that zero states merge and that our 15-state DFA is minimal." | 13-round partition evolution table displayed. |

- **Technical Meaning:** Proves that the application is an authentic educational platform that computes and presents the underlying mathematics transparently.

---

### Demo 5: Testing & Equivalence Verification
- **Presenter:** **Isiah Thomas A. Perito**
- **Goal:** Prove model agreement across the test suite and showcase automated testing.

| Step | Action | Spoken Explanation | Expected UI Result |
|---|---|---|---|
| **1** | Click **Tests** in the navigation sidebar. | "On the Tests page, we maintain 28 predefined edge cases." | Test suite dashboard loads. |
| **2** | Click **Run All Tests**. | "As you can see, all 28 test cases pass instantly. Furthermore, the ε-NFA, subset DFA, and minimal DFA agree 100% on all 28 inputs." | 28 green checkmarks; status indicator reads: `28/28 passed · All 3 models agree`. |
| **3** | (Optional / If asked) Open terminal and run `pytest`. | "Behind the GUI, our automated pytest suite runs over 250 automated tests, including differential checks against Python's regex." | Terminal outputs 279 passing tests in under 30 seconds. |

---

## Part 3: Team Member Responsibilities & Defense Roster

All six team members must speak during the presentation and defend their respective domains during the Q&A session.

| Team Member | Official Role | Presentation Responsibilities | Primary Defense Domain (Q&A) |
|---|---|---|---|
| **Talingting, Ken Ira L.** | **Project Leader** | Slide 1 (Intro) · Slide 14 (Conclusion & Wrap-up) | Project management, scope, high-level architecture, general questions |
| **Anub, Mark Christian T.** | **Language Analyst · DFA Designer** | Slide 2 (Language) · Slide 11 (Rejection theory) | Alphabet $\Sigma$, language cardinality, regular language theorems, ASCII boundaries |
| **Dotosme, James Paul B.** | **Presentation Lead** | Slide 3 (Pipeline) · Slide 9 (Interface) · Slide 10 (Valid Demo) | GUI features, presentation flow, user interaction, demo execution |
| **Lauzon, Chester Josh C.** | **Programmer · Automata Optimizer** | Slides 4, 5, 6 (NFA, DFA, Minimization) · Slide 8 (Architecture) · Slide 13 (Engineering) | Core algorithms, Thompson construction, subset construction, Moore minimization, proof of minimality, software architecture |
| **Perito, Isiah Thomas A.** | **Tester · QA** | Slide 7 (Verification) · Slide 12 (Testing) | Product automaton BFS proof, differential testing, `re.fullmatch`, mutation testing, edge cases |
| **Ayson, Rey Noel C.** | **Documentation** | Slide 13 (Docs & Accessibility) · Presentation Support | Markdown generation, automated doc checks, diagrams, accessibility, slide coordination |

---

## Part 4: Who Answers Which Question? (Quick Delegation Guide)

When the panel asks a question, **Ken Talingting (Team Leader)** should acknowledge the question and either answer directly or delegate smoothly to the designated expert:

- **Questions on Alphabet, Language, or Math Properties:** $\implies$ **Mark Anub**
  - *"Why is the language regular?"*
  - *"Why is the alphabet limited to 14 symbols?"*
  - *"What if we allowed lowercase letters?"*
- **Questions on NFA, DFA, Minimization, or Algorithms:** $\implies$ **Chester Lauzon**
  - *"Why did zero states merge?"*
  - *"Why does the NFA have 26 states?"*
  - *"Explain the shortest accepting distance proof."*
  - *"Why is there a trap state?"*
- **Questions on Testing, Proofs, or Oracle Disagreements:** $\implies$ **Isiah Perito**
  - *"How does the product automaton prove equivalence?"*
  - *"What is differential testing?"*
  - *"Why test against `re.fullmatch`?"*
  - *"How did you test Unicode look-alikes?"*
- **Questions on UI, User Experience, or Demo Behavior:** $\implies$ **James Dotosme**
  - *"How does the tape widget work?"*
  - *"Can a user step backward?"*
  - *"Why doesn't the simulator auto-trim spaces?"*
- **Questions on Documentation, Diagrams, or Architecture:** $\implies$ **Rey Ayson & Chester Lauzon**
  - *"How are the diagrams generated?"*
  - *"How do you keep docs in sync with code?"*
