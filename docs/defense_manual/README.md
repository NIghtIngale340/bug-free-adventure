# Defense Manual — Smart Employee ID Validator (CCAUTOMA)

**What this folder is:** the complete study guide, presentation script, technical explanation and defense
reviewer for our project, in one place. It follows the slides in our PPTX (`automata.pptx`, 14 slides), and
every technical claim was checked against the code in this repository.

**Who it is for:** all six of us. You do not need to know automata theory before reading it. Each hard idea is
explained in plain English first, then technically.

## How to read it

**Status:** Complete! All files 01 through 10 are fully written, cross-verified against the codebase, and linked together.

### Step-by-Step Reading Roadmap: What to Read First, Next, and in Sequence

To master the project without getting overwhelmed, follow this structured, 5-stage reading sequence:

#### 🏁 Step 1: Foundational Context (Start Here)
1. **First:** [01 — Project Context](01_project_context.md)  
   *What you learn:* What the project is, why it's not "just an ID validator", the high-level compilation pipeline, and simple analogies for every stage.
2. **Next:** [02 — The Formal Language](02_formal_language.md)  
   *What you learn:* What an alphabet and language are, why $|\Sigma| = 14$, why $|L| = 10^8$, why finite languages are regular, and why `EMP-YYYY-NNNN` is a mathematical language, not just an informal string format.

#### ⚙️ Step 2: Core Automata Theory & Verification (The Core Math)
3. **Next:** [03 — Automata Theory](03_automata_theory.md)  
   *What you learn:* The beginner FAQ (Thompson atom, authoritative minimal DFA, NFA vs DFA steps), Regex AST $\to$ Thompson $\varepsilon$-NFA (26 states) $\to$ Subset DFA (15 states) $\to$ Moore minimization (13 rounds, 0 merges), and the shortest-accepting-distance minimality proof.
4. **Next:** [04 — Verification & Correctness](04_verification.md)  
   *What you learn:* How we proved the DFA correct: Product Automaton BFS ($15 \times 15$ Cartesian product) vs Differential Testing against Python's `re.fullmatch` on 61,371+ inputs.

#### 💻 Step 3: Software Architecture & Concrete Traces (How It Runs)
5. **Next:** [05 — Software Architecture](05_architecture.md)  
   *What you learn:* The three tiers (GUI $\to$ Services $\to$ Core), why the GUI contains 0 automata logic, and why `app.core.simulator.Run` is the single source of truth.
6. **Next:** [06 — Validation Flows](06_validation_flows.md)  
   *What you learn:* Follow exact traces for valid inputs (`EMP-2026-0042`), structural errors (`EMP2026-0001` $\to q_{\text{trap}}$), alphabet errors (`EMP-2026-12A4`), and whitespace errors, plus the complete system startup lifecycle.

#### 🎙️ Step 4: Defense Rehearsal & Live Demonstration (What to Say & Do)
7. **Next:** [07 — Presentation Flow](07_presentation_flow.md)  
   *What you learn:* The slide-by-slide script for all 14 slides (exact wording, transitions, and slide emphasis), plus the 8–10 minute defense schedule.
8. **Next:** [08 — Live Demo & Roles](08_live_demo.md)  
   *What you learn:* The 5 live demo protocols, keyboard shortcuts, recovery fallbacks if the app misbehaves, team member duties, and who answers which panel questions.

#### 🎓 Step 5: Final Defense Readiness & Q&A Mastery (Cram & Drill)
9. **Next:** [09 — Q&A Bank](09_qa_bank.md)  
   *What you learn:* 30+ categorized defense questions across 10 categories (A to J) including "Panel Trap" questions, each with Short Answer, Expanded Explanation, Owner, and Key Terms.
10. **Finally:** [10 — Reviewer](10_reviewer.md)  
    *What you learn:* The compact cheat sheet: must-memorize facts and numbers, must-understand proofs, and the emergency 60-second explanation.

---

### Alternative Tracks: Choose Your Speed

- **⏱️ Track A: The Emergency 30-Minute Cram:**
  1. [10 — Reviewer](10_reviewer.md) (15 mins — memorize numbers and proofs)
  2. [07 — Presentation Flow](07_presentation_flow.md) (10 mins — read your own slide scripts)
  3. [08 — Live Demo](08_live_demo.md) (5 mins — know your demo cue and recovery steps)
- **⏱️ Track B: The 1-Hour Comprehensive Review:**
  1. [01 — Project Context](01_project_context.md) $\to$ 2. [03 — Automata Theory](03_automata_theory.md) $\to$ 3. [07 — Presentation Flow](07_presentation_flow.md) $\to$ 4. [09 — Q&A Bank](09_qa_bank.md) $\to$ 5. [10 — Reviewer](10_reviewer.md).
- **👥 Track C: Role-Specific Reading Plan:**
  - **Ken Talingting (Leader):** 01 $\to$ 07 (Slides 1 & 14) $\to$ 08 $\to$ 09 (Cat A, J) $\to$ 10
  - **Mark Anub (Language Analyst):** 02 $\to$ 03 $\to$ 06 $\to$ 07 (Slides 2 & 11) $\to$ 09 (Cat B)
  - **Chester Lauzon (Programmer/Optimizer):** 03 $\to$ 05 $\to$ 07 (Slides 4, 5, 6, 8, 13) $\to$ 09 (Cat C, D, E, F, H)
  - **Isiah Perito (QA/Tester):** 04 $\to$ 07 (Slides 7 & 12) $\to$ 08 (Demo 5) $\to$ 09 (Cat G, I)
  - **James Dotosme (Presentation Lead):** 07 $\to$ 08 (Demos 1 & 2) $\to$ 09 $\to$ 10
  - **Rey Ayson (Documentation):** 01 $\to$ 07 (Slide 13) $\to$ 08 $\to$ 10

---

### Complete File Index

| # | File | What you get |
|---|---|---|
| 01 | [Project Context](01_project_context.md) | What the project is, why it exists, the full pipeline stage by stage |
| 02 | [Formal Language](02_formal_language.md) | Σ, L, \|Σ\| = 14, \|L\| = 10⁸, finite ⇒ regular |
| 03 | [Automata Theory](03_automata_theory.md) | Beginner FAQ, Regex AST, Thompson ε-NFA (26), subset DFA (15), Moore minimization (13 rounds, 0 merges) |
| 04 | [Verification](04_verification.md) | Product-automaton proof vs differential testing |
| 05 | [Software Architecture](05_architecture.md) | GUI → Services → Core, where everything lives |
| 06 | [Validation Flows](06_validation_flows.md) | Exactly what happens for `EMP-2026-0042` and invalid inputs, plus "What actually happens inside the system?" |
| 07 | [Presentation Flow](07_presentation_flow.md) | Slide-by-slide script + minute-by-minute timeline |
| 08 | [Live Demo & Roles](08_live_demo.md) | Demo procedure with recovery steps, who does what |
| 09 | [Q&A Bank](09_qa_bank.md) | Exhaustive defense questions in 10 categories, with short answer, expansion, owner, key terms |
| 10 | [Reviewer](10_reviewer.md) | Must-memorize facts, top 20 questions, 60-second explanation |

## The team

| Member | Role (from the PPTX) |
|---|---|
| Anub, Mark Christian T. | Language Analyst · DFA Designer |
| Ayson, Rey Noel C. | Documentation |
| Dotosme, James Paul B. | Presentation Lead |
| Lauzon, Chester Josh C. | Programmer · Automata Optimizer |
| Perito, Isiah Thomas A. | Tester · QA |
| Talingting, Ken Ira L. | Project Leader |

## State-name cheat sheet (read this first, it prevents confusion)

The project uses three naming schemes. They are **different machines**, not typos:

| Prefix | Machine | Example | Where you see it |
|---|---|---|---|
| `n` | ε-NFA from Thompson's construction | `n0` … `n25` | Slide 4, Theory → ε-NFA |
| `D` | DFA from subset construction (before minimization) | `D0` … `D13`, `D_trap` | Slides 5–6, Theory → Subset construction / DFA |
| `q` | Minimal DFA (what the simulator runs) | `q0` … `q13`, `q_trap` | Slides 10–11, Simulate page |

`Di` and `qi` are the same state under a new name — minimization merged nothing, it only renamed.

## Sources and accuracy

Primary sources, in order of authority:

1. **The code** (`app/`) and **tests** (`tests/`) — these decide what is true.
2. **The PPTX** (14 slides + speaker notes) — the presentation structure.
3. **The project docs** (`docs/*.md`, `README.md`) — generated tables are checked against the code by `tests/test_docs.py`.

Re-verified on **2026-10-08**: `python -m pytest` → **279 passed**; `python scripts/gen_docs.py --check` → no stale tables.

When something could not be confirmed from these sources, this manual says so with:
> **Not confirmed by the provided project materials.**

### Inconsistencies we found (know these before the panel does)

| # | What | Which is right | What to say if asked |
|---|---|---|---|
| 1 | `docs/contributions.md` and `docs/DEFENSE_SCRIPT_AND_QA.md` describe an older **3-person** split (Ken backend, Chester frontend, "Integrator"). | The PPTX's **6-member** roles. This manual follows the PPTX. | Fix `contributions.md` before submission (the file itself says the team must review it). |
| 2 | Git commit `e5bf8b3` says "Hopcroft DFA minimization". | The current code (`app/core/minimizer.py`) uses **Moore** partition refinement. | "We use Moore's algorithm. Hopcroft's computes the same partition faster; with 15 states the difference doesn't matter." |
| 3 | Error positions such as "`'A'` at position 11". | Positions are **0-based** (counting starts at 0). `A` is the 12th character. | "Positions are zero-indexed, like Python string indices." |
| 4 | Slide 11 says the trap state "stays there". | Mathematically true: δ(q_trap, a) = q_trap. The **simulator stops reading** as soon as it enters the trap, because the result can no longer change. | "Once in the trap, rejection is certain, so the run ends there. The full DFA still has the self-loops." |
| 5 | Slide 12 says "250+ automated tests". | 279 on 2026-10-08. "250+" is still accurate. | Say "over 250", or "279 at last run". |
| 6 | Slide 13 says "reduced-motion support". | It's an **environment variable** (`CAUTOMA_REDUCE_MOTION=1`), not a button in the GUI. | Don't promise a settings toggle. |
