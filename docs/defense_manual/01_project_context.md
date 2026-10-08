# 01 — Complete Project Context

[← Index](README.md) · Next: [02 Formal Language →](02_formal_language.md)

---

## 1. What is this project?

### In one sentence

The **Smart Employee ID Validator** is a desktop program that checks whether a typed string, such as
`EMP-2026-0042`, is a correctly formatted employee ID, and **shows you, step by step, how a machine made that decision**.

### In plain English

Imagine an organization where every employee ID looks like this:

```text
EMP-2026-0042
│   │    └── 4-digit employee number
│   └─────── 4-digit year
└─────────── the fixed prefix "EMP"
```

HR staff type these IDs by hand, and people make typos: `EMP2026-0042` (missing hyphen), `emp-2026-0042`
(lowercase), `EMP-2026-42` (too short), a stray space at the end. Our program reads what was typed and answers
**ACCEPTED** or **REJECTED**, and when it rejects, it tells you **exactly where and why**.

### What the user does

1. Opens the app (`python -m app.main`).
2. Types an ID on the **Simulate** page and presses **Enter** (or **Load**).
3. Presses **Step** (one symbol at a time), **Play** (animated) or **Run all** (instant).
4. Watches the tape, the state diagram and the transition history.
5. Reads the verdict: ACCEPTED or REJECTED, with a reason.

The user can also open the **Theory** page (every construction stage with tables and diagrams) and the **Tests**
page (28 predefined cases and batch validation).

### What the system produces

For every input, a structured result (`SimulationResult` in `app/core/models.py`) containing:

- accepted or not, and a **status**: `ACCEPTED`, `REJECTED_INVALID_SYMBOL`, `REJECTED_NO_TRANSITION`,
  `REJECTED_NON_FINAL_STATE` or `REJECTED_EMPTY_INPUT`
- the final state reached
- the full **trace**: every transition taken, symbol by symbol
- the error position and a human-readable explanation

### Why is this related to Formal Languages and Automata Theory?

Because the set of valid IDs **is a formal language**, and the program that recognizes it **is a finite automaton**.

Think of it this way:
- A **language** (in this course) is just a set of strings. "All valid employee IDs" is a set of strings, so it's a language.
- An **automaton** is an abstract machine that reads a string one symbol at a time and ends up saying yes or no.
- Automata theory tells us *which* languages a simple machine can recognize, and *how to build* that machine.

Our project applies all of this to a real, practical format.

---

## 2. The main idea: we are not "just" making a validator

Python can check this format in one line:

```python
re.fullmatch(r"EMP-[0-9]{4}-[0-9]{4}", text)
```

So why build a whole project? Because **the validator is the excuse, not the point.**

The point is to demonstrate this:

> A formal language can be transformed **mathematically, by algorithms**, into an executable automaton, and that
> automaton can be implemented as working, inspectable software.

In our project:
- We **wrote down the language once**, as a regular expression (`ID_REGEX` in `app/data/id_rules.py`).
- **Algorithms built every machine from it**: the ε-NFA, the DFA and the minimal DFA.
- **Nobody typed a transition table by hand** for the validator. (A hand-written table exists, but only to
  cross-check the derived machine in tests. The simulator never reads it.)
- We **proved** the machines are equivalent and that the final DFA is minimal.
- The GUI lets you **watch** the automaton work.

### Why that matters academically

In class, these algorithms (Thompson's construction, subset construction, minimization) are usually done on
paper with small examples. Our project shows them working **end-to-end on a real language**, with every
intermediate result visible and checked. It turns textbook theorems into running code, and it shows the theory
holds up: change the regex and every machine is rebuilt automatically.

> **Line to remember (from slide 1):** "This is not just a validator. It is a formal language turned into an
> executable automaton, algorithmically."

---

## 3. What happens from input to result?

### The simple flow (what the user experiences)

```text
User enters Employee ID
        ↓
Alphabet validation        ← "Is every character one of the 14 allowed symbols?"
        ↓
Automaton processing       ← the DFA starts in q0
        ↓
State transitions          ← one transition per symbol: q0 → q1 → q2 → …
        ↓
Accept / Reject            ← did we finish in the accepting state q13?
        ↓
GUI displays the result    ← verdict banner, highlighted path, history
```

### The deeper technical pipeline (what the program builds)

```text
Formal Language            L = { EMP-d₁d₂d₃d₄-d₅d₆d₇d₈ }
      ↓
Regular Expression         EMP-D⁴-D⁴,  D = (0∪1∪…∪9)
      ↓
Regex AST                  a tree of Lit / Class / Repeat / Concat nodes
      ↓  thompson()
ε-NFA                      26 states, 12 ε-transitions
      ↓  subset_construction()
DFA                        15 states (14 live + D_trap)
      ↓  minimize()
Minimal DFA                15 states (0 merged, 13 refinement rounds)
      ↓  dfa_equivalent()
Equivalence Verification   product automaton BFS: 15 pairs, EQUAL
      ↓
Simulation Engine          app.core.simulator.Run
      ↓
PySide6 GUI                Simulate · Theory · Tests
```

All of this is done in `app/core/pipeline.py::build_pipeline`, once, when the program first needs it (the
result is cached).

### Every stage explained

| Stage | What it is | Why it exists | In → Out | Analogy |
|---|---|---|---|---|
| **Formal language** | The exact set of valid strings, written in math | So "valid" has one precise meaning | Idea → set `L` | The law that says what counts as a valid ID |
| **Regular expression** | A compact formula describing `L` using concatenation, union and repetition | A machine can't be built from English; it can from a regex | `L` → `EMP-D⁴-D⁴` | A recipe |
| **Regex AST** | The regex stored as a tree in code | Algorithms walk trees, not text | regex → tree (`Concat`, `Lit`, `Class`, `Repeat`) | The recipe broken into numbered steps |
| **ε-NFA** | A machine that may be in several states at once and may move without reading (ε) | Thompson's construction turns a regex into one mechanically | AST → 26-state ε-NFA | A rough draft that's easy to write |
| **DFA** | A machine that is in exactly one state at any time | Computers run deterministic machines easily: one lookup per symbol | ε-NFA → 15-state DFA | The clean copy of the draft |
| **DFA minimization** | Merging states that behave identically | To get the smallest DFA, and to *prove* it's the smallest | DFA → minimal DFA (still 15) | Editing out repeated paragraphs (here there were none) |
| **Equivalence verification** | Checking two machines accept exactly the same strings | So we know minimization didn't break anything | two DFAs → EQUAL / counterexample | Comparing two answer keys line by line |
| **Simulation engine** | Code that runs the DFA on an input, symbol by symbol, recording every step | One trusted runner for everything | DFA + input → `SimulationResult` | Actually playing the game by the rules |
| **PySide6 GUI** | The window the user sees | To make the theory observable | `SimulationResult` → pictures, verdict | The scoreboard |

**How they connect:** each stage's output is the next stage's input. That's why the slide says "26 → 15 → 15":
the numbers are the size of each stage's output.

---

## 4. Where to go next

- The language itself, in depth → [02 Formal Language](02_formal_language.md)
- How each construction works → [03 Automata Theory](03_automata_theory.md)
