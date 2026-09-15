# CCAUTOMA – Employee ID Validator
## Project Specification, Workload Allocation, Technical Plan, and Programmer Prompt

**Course:** CCAUTOMA – 1st AY 2026  
**Project:** Employee ID Validator – Organization-defined ID Structure  
**Primary Language:** Python 3.12+  
**Recommended UI:** PySide6 (Qt for Python)  
**Defense Dates:** September 29 and October 2, 2026  

---

# 1. Project Overview

Build a **Smart Employee ID Validator** that recognizes whether an employee ID belongs to an organization-defined formal language.

The project is primarily an **Automata Theory application**, not a production HR system. The software should make the underlying theory visible and understandable rather than hiding all automata logic behind a simple “valid/invalid” result.

The system must demonstrate the complete pipeline required by the course:

```text
Organization ID Rules
        ↓
Formal Language Definition
        ↓
Regular Expression
        ↓
NFA
        ↓
NFA → DFA (Subset Construction)
        ↓
DFA Minimization
        ↓
Minimized DFA
        ↓
Python Simulator + GUI
```

The most important feature is a **visual simulator** where a user enters an Employee ID and can see the input being processed symbol-by-symbol, the current state, the next state, and the final ACCEPTED/REJECTED decision.

---

# 2. Project Goal

Create a small but polished educational application that allows a user to:

1. Enter an Employee ID.
2. Validate the input against the defined alphabet.
3. Process the ID using the **minimized DFA**.
4. Show the state transition path step-by-step.
5. Highlight the current state during simulation.
6. Display the final state.
7. Clearly show **ACCEPTED** or **REJECTED**.
8. Explain *why* the input was accepted or rejected.
9. Test multiple Employee IDs.
10. View the formal language, RE, NFA, DFA, and minimized DFA used by the project.

The GUI should support the academic defense by making it easy to explain what happens **under the hood**.

---

# 3. Recommended Example ID Rule

The exact organization-defined structure should be agreed upon by the group before implementation. A simple example that is suitable for a first project is:

```text
EMP-YYYY-NNNN
```

Where:

- `EMP` is a fixed prefix.
- `YYYY` is a four-digit year.
- `NNNN` is a four-digit employee number.
- Hyphens are required.
- Only the defined symbols are accepted.

Example accepted strings:

```text
EMP-2026-0001
EMP-2026-0123
EMP-2026-9999
EMP-2027-1000
```

Example rejected strings:

```text
EMP2026-0001       # Missing first hyphen
EMP-26-0001        # Incorrect year length
EMP-2026-123       # Employee number too short
emp-2026-0001      # Wrong capitalization
EMP-2026-12A4      # Invalid symbol
EMP-2026-00001     # Employee number too long
```

> **Important:** Treat this only as a starting example. The final group should choose one clear organization-defined rule and use that exact rule consistently across the RE, NFA, DFA, minimized DFA, source code, test cases, and documentation.

---

# 4. Formal Language Requirements

The project must formally define:

## 4.1 Alphabet

Define the complete alphabet Σ used by the validator.

For example:

```text
Σ = {E, M, P, 0, 1, 2, ..., 9, -}
```

The implementation must reject symbols outside Σ.

## 4.2 Language

Define:

```text
L = { all strings that follow the organization-defined Employee ID structure }
```

Provide at least:

- 10 accepted strings
- 10 rejected strings

## 4.3 Regular Expression

Write one RE that describes the language. Explain each component.

## 4.4 NFA

Provide:

- Q
- Σ
- δ
- q0
- F
- Transition table
- State diagram

Formally:

```text
M = (Q, Σ, δ, q0, F)
```

## 4.5 NFA-to-DFA

Use subset construction and show the actual conversion process, not just the final DFA.

## 4.6 DFA Minimization

Show:

1. Unreachable states, if any.
2. Initial partitioning into final/non-final states.
3. Refinement of partitions.
4. Equivalent states.
5. State merging.
6. Final minimized DFA.

The final simulator should use the **minimized DFA** as the authoritative recognizer.

---

# 5. Recommended Technology Stack

## Core

- **Python 3.12+**
- Standard library where practical
- `dataclasses` for automata data structures
- `enum` for state/result types where useful

## GUI

### Recommended: PySide6

Why:

- Professional-looking desktop UI.
- Native Qt widgets.
- Easy table, tabs, status indicators, and layouts.
- Suitable for a classroom project without requiring a backend server.
- Easier to produce a polished demo than a command-line application.

Alternative options:

- **Tkinter:** simplest, but less polished.
- **CustomTkinter:** simpler modern styling, but adds another dependency.
- **Streamlit:** excellent for quick demos, but less suitable for a desktop-style automata simulator.

## Visualization

Recommended:

- `graphviz` for automata diagrams.
- `pydot` or Graphviz Python bindings where needed.
- Qt graphics widgets if interactive state highlighting is implemented directly.

## Testing

- `pytest`
- Optional `pytest-cov`

## Code Quality

- `ruff` for linting/formatting.
- Type hints throughout core modules.
- Git + GitHub for collaboration.

## Documentation

- Markdown (`.md`)
- Mermaid diagrams for architecture/workflows where appropriate.
- Export important diagrams to PNG/SVG for the final report if needed.

---

# 6. Recommended System Architecture

Keep the project modular. Do **not** put the automata logic directly inside the GUI event handlers.

```text
┌──────────────────────────────────────────────┐
│                  GUI / PySide6               │
│                                              │
│  Input │ Simulation │ Automata │ Help/Docs   │
└──────────────────────┬───────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────┐
│                Application Layer             │
│                                              │
│ Validation Service │ Simulation Controller   │
└──────────────────────┬───────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────┐
│                 Automata Core                │
│                                              │
│ Language │ RE │ NFA │ DFA │ Minimization    │
│ Transition Engine │ Acceptance Logic         │
└──────────────────────┬───────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────┐
│            Data / Configuration              │
│                                              │
│ ID rules │ states │ transitions │ test data  │
└──────────────────────────────────────────────┘
```

The GUI should consume clean, structured results from the automata engine.

---

# 7. Recommended Repository Structure

```text
employee-id-validator/
│
├── README.md
├── PROJECT_SPEC.md
├── requirements.txt
├── pyproject.toml
├── .gitignore
│
├── app/
│   ├── __init__.py
│   ├── main.py
│   │
│   ├── core/
│   │   ├── __init__.py
│   │   ├── language.py
│   │   ├── regex_rules.py
│   │   ├── nfa.py
│   │   ├── dfa.py
│   │   ├── minimizer.py
│   │   ├── simulator.py
│   │   └── models.py
│   │
│   ├── services/
│   │   ├── validation_service.py
│   │   └── simulation_service.py
│   │
│   ├── gui/
│   │   ├── main_window.py
│   │   ├── pages/
│   │   │   ├── validator_page.py
│   │   │   ├── simulator_page.py
│   │   │   ├── automata_page.py
│   │   │   └── about_page.py
│   │   ├── widgets/
│   │   │   ├── result_card.py
│   │   │   ├── transition_table.py
│   │   │   └── state_view.py
│   │   └── styles/
│   │       └── theme.qss
│   │
│   └── data/
│       ├── id_rules.py
│       └── test_cases.py
│
├── tests/
│   ├── test_language.py
│   ├── test_dfa.py
│   ├── test_minimization.py
│   └── test_simulator.py
│
├── docs/
│   ├── formal_language.md
│   ├── regex.md
│   ├── nfa.md
│   ├── dfa.md
│   ├── minimization.md
│   ├── testing.md
│   └── contributions.md
│
└── assets/
    ├── diagrams/
    └── screenshots/
```

---

# 8. GUI Requirements

The GUI does not need to be large. It needs to be clear, demonstrable, and directly connected to the Automata Theory concepts.

## Page 1 – Validator Dashboard

Main elements:

- Project title.
- Employee ID input field.
- `Validate` button.
- `Clear` button.
- Large result indicator:
  - ACCEPTED
  - REJECTED
- Short explanation of the result.
- Current state.
- Final state.
- Number of symbols processed.

Example:

```text
Employee ID: [ EMP-2026-0042 ]  [Validate]

Result:        ✓ ACCEPTED
Final State:   q10
Symbols:       12 / 12
Explanation:   The input reached an accepting state.
```

## Page 2 – DFA Simulator

This is the most important educational page.

Show:

- Input string.
- Current symbol.
- Current state.
- Next state.
- Transition history.
- Current DFA state highlighted visually.
- Final result.

Example transition table:

| Step | Symbol | Current State | Next State |
|---:|---|---|---|
| 1 | E | q0 | q1 |
| 2 | M | q1 | q2 |
| 3 | P | q2 | q3 |
| 4 | - | q3 | q4 |
| ... | ... | ... | ... |

Provide controls such as:

```text
[Start] [Next Step] [Run All] [Reset]
```

The `Next Step` button is strongly recommended because it makes the DFA process easy to defend during the oral presentation.

## Page 3 – Automata Information

Use tabs or sections for:

- Formal Language
- Regular Expression
- NFA
- DFA
- Minimized DFA

Show transition tables and diagrams without overwhelming the user.

## Page 4 – Test Cases

Display predefined accepted/rejected examples.

Allow the user to run all test cases and see whether the implementation agrees with the expected result.

---

# 9. Important UI/UX Rules

The interface should be:

- Simple.
- Academic/professional.
- Easy to demonstrate.
- Clearly labeled.
- Not overloaded with unnecessary icons.
- Focused on the automata process.

Avoid:

- Excessive animations.
- Gaming-style UI.
- Too many screens.
- Unrelated features.
- Fake AI/ML features.
- A database unless the group has a real academic reason to use one.

The project is an **Automata Theory simulator**, so correctness and explainability matter more than visual complexity.

---

# 10. Core Programming Responsibilities

## Language Module

Store the organization rule and alphabet in a structured form.

Expected responsibilities:

- Define Σ.
- Define accepted pattern.
- Define example strings.
- Validate symbols.

## NFA Module

Represent:

```text
Q
Σ
δ
q0
F
```

Provide methods for:

- Adding states.
- Adding transitions.
- Inspecting transitions.
- Exporting a transition table.
- Exporting data suitable for visualization.

## DFA Module

Represent deterministic transitions:

```text
δ(q, a) = q'
```

Provide a deterministic simulation method.

## NFA-to-DFA Module

Implement subset construction in a transparent way.

The implementation should preserve information about:

- Original NFA state subsets.
- Generated DFA states.
- Transitions.
- Accepting states.

This information may be displayed in the documentation/debug view.

## Minimization Module

Implement DFA minimization and keep enough metadata to explain which original states were merged.

## Simulator Module

Input:

```text
input_string
```

Output a structured trace such as:

```python
[
    {
        "step": 1,
        "symbol": "E",
        "from_state": "q0",
        "to_state": "q1",
    },
    ...
]
```

Also return:

- Final state.
- Accepted/rejected status.
- Error information when an invalid symbol is encountered.

---

# 11. Validation vs. Automata Simulation

Keep these concepts separate.

### Layer 1 – Alphabet Validation

Check whether every input symbol belongs to Σ.

### Layer 2 – Automata Processing

Run the input through the minimized DFA symbol-by-symbol.

### Layer 3 – Result Presentation

Translate the automata result into a user-friendly message.

This separation makes the code easier to test and defend.

---

# 12. Error Handling Requirements

The application should distinguish between:

### Invalid Symbol

Example:

```text
EMP-2026-12A4
```

If `A` is not in the alphabet for that position/rule, explain that the symbol is invalid.

### Valid Alphabet, Wrong Structure

Example:

```text
EMP2026-0001
```

All symbols may be valid individually, but the overall sequence does not belong to the language.

### Empty Input

Display a clear message and do not attempt normal simulation.

---

# 13. Testing Strategy

The test plan must cover both normal and edge cases.

Minimum recommended categories:

1. Valid standard IDs.
2. Invalid prefix.
3. Wrong year length.
4. Wrong employee-number length.
5. Missing separator.
6. Extra separator.
7. Lowercase/uppercase mismatch.
8. Invalid symbols.
9. Empty input.
10. Boundary numeric values.
11. Very long input.
12. Multiple consecutive invalid inputs.

Every test should record:

| Test ID | Input | Expected | Actual | Pass/Fail |
|---|---|---|---|---|
| TC-001 | EMP-2026-0001 | Accepted | Accepted | PASS |

The test suite must verify that the GUI result and the underlying simulator result agree.

---

# 14. Eight-Member Workload Allocation

The team should avoid making one student responsible for the entire programming task. Each member owns a clearly measurable deliverable while still reviewing the whole project.

## Member 1 – Project Lead / Integrator

### Main responsibilities

- Coordinate the whole project.
- Maintain task board and deadlines.
- Merge contributions.
- Resolve integration conflicts.
- Maintain the final project structure.
- Verify that every course requirement is represented in the implementation and documentation.

### Deliverables

- Master task board.
- Final integration branch.
- Release checklist.
- Final contribution matrix.

---

## Member 2 – Formal Language Analyst

### Main responsibilities

- Define the Employee ID problem.
- Define Σ.
- Define L.
- Produce accepted/rejected examples.
- Confirm exact organizational ID rules.

### Deliverables

- `docs/formal_language.md`
- Accepted/rejected dataset.
- Formal problem definition section.

---

## Member 3 – RE + NFA Designer

### Main responsibilities

- Construct the Regular Expression.
- Explain RE components.
- Design NFA.
- Verify NFA transitions.
- Prepare NFA diagram.

### Deliverables

- `docs/regex.md`
- `docs/nfa.md`
- NFA transition table.
- NFA state diagram.

---

## Member 4 – DFA Conversion Engineer

### Main responsibilities

- Perform subset construction.
- Enumerate reachable subsets.
- Build DFA transition table.
- Verify DFA acceptance matches the NFA.

### Deliverables

- `docs/dfa.md`
- Subset construction table.
- DFA transition table.
- DFA diagram.

---

## Member 5 – DFA Minimization Engineer

### Main responsibilities

- Remove unreachable states.
- Perform state partitioning.
- Identify equivalent states.
- Build minimized DFA.
- Verify minimized DFA equivalence.

### Deliverables

- `docs/minimization.md`
- Minimization proof/workings.
- Final minimized DFA.
- State-merging record.

---

## Member 6 – Python Automata/Core Developer

### Main responsibilities

- Implement automata data structures.
- Implement DFA simulator.
- Implement transition tracing.
- Implement minimization/conversion logic if automated.
- Write unit tests for core logic.

### Deliverables

- `app/core/`
- `app/services/`
- Core unit tests.
- Sample simulator traces.

---

## Member 7 – GUI Developer + UX Lead

### Main responsibilities

- Build the PySide6 interface.
- Connect GUI to services.
- Build validation screen.
- Build step-by-step DFA simulation screen.
- Display transition history.
- Display accepting/rejecting states.
- Implement clear/reset/test-case interactions.

### Deliverables

- `app/gui/`
- UI screenshots.
- Demo flow.

---

## Member 8 – QA + Documentation + Presentation Lead

### Main responsibilities

- Build test matrix.
- Run integration tests.
- Compare expected and actual automata behavior.
- Collect screenshots.
- Assemble final documentation.
- Prepare presentation slides.
- Prepare defense questions and answers.

### Deliverables

- `tests/`
- `docs/testing.md`
- Final report support materials.
- Presentation checklist.
- Defense question bank.

---

# 15. Shared Responsibility Rule

Although each member has a primary ownership area, **every member must understand the complete pipeline**.

Every team member must be able to explain:

```text
Problem
→ Language
→ RE
→ NFA
→ DFA
→ Minimized DFA
→ Program
→ GUI
```

A good internal rule is:

> **Own one module, review two modules, understand all modules.**

Each member should perform at least one code/research review outside their assigned area.

---

# 16. Git / Collaboration Workflow

Use GitHub.

Recommended branches:

```text
main
│
├── develop
│
├── feature/formal-language
├── feature/nfa
├── feature/dfa
├── feature/minimization
├── feature/core-simulator
├── feature/gui
└── feature/testing-docs
```

Rules:

1. Do not commit directly to `main`.
2. Use pull requests.
3. Use descriptive commit messages.
4. At least one teammate should review significant changes.
5. Keep commits small enough to understand.
6. Never commit generated virtual environments or secrets.

Example commit messages:

```text
feat: add DFA transition simulator
feat: add employee ID language rules
feat: add step-by-step simulation view
fix: handle invalid alphabet symbols
 docs: add subset construction explanation
 test: add boundary employee ID cases
```

---

# 17. Suggested Development Milestones

Because the defense is on **September 29 and October 2, 2026**, the project should be developed in short milestones.

## Milestone 1 – Requirements Freeze

Target: **September 15–17**

Complete:

- Final Employee ID format.
- Final alphabet.
- Initial 10+ accepted and rejected examples.
- Team roles.
- GitHub repository.
- Folder structure.

## Milestone 2 – Automata Design

Target: **September 17–20**

Complete:

- RE.
- NFA.
- DFA conversion.
- DFA minimization.
- Manual verification.

## Milestone 3 – Core Simulator

Target: **September 20–23**

Complete:

- Python automata classes.
- Minimized DFA simulation.
- Trace generation.
- Unit tests.

## Milestone 4 – GUI

Target: **September 22–25**

Complete:

- Validator dashboard.
- Step-by-step simulator.
- Automata information pages.
- Test-case page.

## Milestone 5 – Integration + Documentation

Target: **September 25–27**

Complete:

- Full-system testing.
- Screenshots.
- Report.
- Presentation.
- Defense preparation.

## Milestone 6 – Final Freeze

Target: **September 28**

Complete:

- Bug fixes only.
- Final backup.
- Final demo rehearsal.
- Every member prepares for Q&A.

---

# 18. Minimum Viable Product (MVP)

If time becomes limited, prioritize these features in this order:

### Priority 1 – Required by course

- Correct formal language.
- Correct RE.
- Correct NFA.
- Correct DFA.
- Correct minimization.
- Working simulator.

### Priority 2 – Demo quality

- PySide6 GUI.
- ACCEPTED/REJECTED result.
- Transition trace.
- Current/final state.
- Multiple test cases.

### Priority 3 – Polish

- Interactive DFA diagram.
- Step-by-step animation.
- Export results.
- Theme customization.
- Extra explanations.

Do not sacrifice automata correctness for visual polish.

---

# 19. Documentation Deliverables

The final documentation should map directly to the course requirements.

Recommended report structure:

1. Cover Page
2. Table of Contents
3. Introduction
4. Project Objectives
5. Scope and Limitations
6. Problem Definition
7. Formal Language Definition
8. Alphabet and Strings
9. Accepted and Rejected Inputs
10. Regular Expression
11. NFA Formal Definition
12. NFA Transition Table and Diagram
13. NFA-to-DFA Subset Construction
14. DFA Transition Table and Diagram
15. DFA Minimization
16. Minimized DFA Diagram
17. System Architecture
18. User Interface Design
19. Implementation / Source Code
20. Test Cases and Results
21. Screenshots
22. Discussion of Results
23. Limitations
24. Conclusion
25. References
26. Individual Contribution Matrix

Use **APA format** where required by the course.

---

# 20. Defense Demonstration Flow

The live demo should take approximately 3–4 minutes inside the 8–10 minute presentation portion.

Recommended sequence:

### Step 1 – Show the problem

"We designed an Employee ID Validator for an organization-defined ID structure."

### Step 2 – Show one valid ID

Enter:

```text
EMP-2026-0042
```

Show:

```text
ACCEPTED
```

### Step 3 – Show simulation

Click `Next Step` repeatedly and explain how the input moves through DFA states.

### Step 4 – Show one invalid ID

Enter an invalid structure such as:

```text
EMP-2026-12A4
```

Show the exact point of failure.

### Step 5 – Connect implementation to theory

Explain:

```text
RE → NFA → DFA → Minimized DFA → Python Simulator → GUI
```

This connection should be emphasized because it demonstrates that the GUI is not merely a form validator; it is an implementation of the automaton developed in the course project.

---

# 21. Defense Questions to Prepare For

Every member should be ready to answer questions such as:

### Formal Language

- What is your alphabet?
- What is your language?
- What makes a string valid?
- Why is this a regular language?

### RE

- What does each part of your RE mean?
- Why does this RE reject invalid IDs?

### NFA

- Why did you choose these states?
- Which state is the start state?
- Which states are accepting?

### DFA

- How did subset construction work?
- Why can the DFA only have one transition per symbol from a state?

### Minimization

- Which states were merged?
- Why are those states equivalent?
- How many states did you reduce?

### Implementation

- How does the program simulate the DFA?
- What happens when an unknown symbol is entered?
- Why does the GUI use the minimized DFA?

### Testing

- How do you know the program is correct?
- What edge cases did you test?
- Does the minimized DFA accept exactly the same language as the original DFA?

---

# 22. Definition of Done

The project is considered complete only when all of the following are true:

- [ ] Formal problem definition completed.
- [ ] Alphabet Σ finalized.
- [ ] Language L finalized.
- [ ] 10+ accepted examples.
- [ ] 10+ rejected examples.
- [ ] Regular Expression completed and explained.
- [ ] NFA formally defined.
- [ ] NFA transition table completed.
- [ ] NFA diagram completed.
- [ ] Subset construction documented.
- [ ] DFA completed.
- [ ] DFA diagram completed.
- [ ] DFA minimized.
- [ ] Minimized DFA documented.
- [ ] Python simulator works.
- [ ] Symbol-by-symbol tracing works.
- [ ] GUI works.
- [ ] Multiple test cases work.
- [ ] Unit tests pass.
- [ ] Screenshots captured.
- [ ] Final documentation completed.
- [ ] Presentation completed.
- [ ] Every member can explain the complete system.

---

# 23. Programmer AI Prompt

Copy the following section into an AI coding assistant when asking it to help implement the project.

---

## MASTER IMPLEMENTATION PROMPT

You are the lead Python software engineer helping a university group build an **Automata Theory course project** called **Employee ID Validator**.

The project is an educational application whose purpose is to demonstrate how a practical input-validation problem can be represented as a formal language and recognized using finite automata.

### Academic requirements

The final project must demonstrate:

1. Problem definition.
2. Alphabet Σ.
3. Language L.
4. Accepted and rejected strings.
5. Regular Expression.
6. NFA.
7. NFA transition table and state diagram.
8. NFA-to-DFA conversion using subset construction.
9. DFA transition table and state diagram.
10. DFA minimization.
11. Minimized DFA.
12. Working program that simulates the minimized DFA.
13. User input.
14. Symbol validation.
15. Symbol-by-symbol state transitions.
16. Final state.
17. ACCEPTED/REJECTED result.
18. Multiple test cases.

### Technical direction

Use:

- Python 3.12+
- PySide6 for the GUI
- pytest for testing
- Graphviz for automata diagrams where appropriate
- Type hints
- dataclasses where useful
- GitHub-friendly modular architecture

Do not create a web backend unless specifically requested. The default application should run locally as a Python desktop application.

### Architecture rules

Separate the system into:

```text
GUI
↓
Application/Service Layer
↓
Automata Core
↓
Data/Configuration
```

The GUI must never contain the actual DFA algorithm.

The DFA simulator must be independently testable without starting the GUI.

### Functional behavior

The user enters an Employee ID.

The application must:

1. Check for empty input.
2. Check whether symbols belong to the defined alphabet.
3. Run the minimized DFA symbol-by-symbol.
4. Record each transition.
5. Return the final state.
6. Determine whether the final state is accepting.
7. Display ACCEPTED or REJECTED.
8. Explain the failure when useful.

Return structured simulation data rather than only a Boolean.

Example:

```python
SimulationResult(
    input_string="EMP-2026-0042",
    accepted=True,
    final_state="q_final",
    trace=[...],
    error=None,
)
```

### Simulation trace

Each transition should contain:

```python
{
    "step": 1,
    "symbol": "E",
    "from_state": "q0",
    "to_state": "q1",
}
```

The GUI will use this data to build a transition table and step-by-step simulator.

### GUI requirements

Build a clean academic interface with four main views:

1. **Validator**
   - Employee ID input.
   - Validate button.
   - ACCEPTED/REJECTED result.
   - Final state.
   - Short explanation.

2. **DFA Simulator**
   - Input string.
   - Transition history.
   - Current state.
   - Current symbol.
   - Next state.
   - `Start`, `Next Step`, `Run All`, and `Reset` controls.

3. **Automata**
   - Formal language information.
   - RE.
   - NFA information.
   - DFA information.
   - Minimized DFA information.
   - Transition tables.
   - Diagrams where available.

4. **Test Cases**
   - Predefined examples.
   - Expected result.
   - Actual result.
   - Pass/Fail indicator.

### Design requirements

Prioritize:

- clarity
- correctness
- academic usability
- easy live demonstration
- explainability

Avoid:

- unnecessary animations
- excessive icons
- fake AI features
- database features that are unrelated to the course
- over-engineering

### Coding requirements

Generate maintainable code.

Use small classes/functions with clear responsibilities.

Add type hints.

Add docstrings for important public classes/functions.

Avoid hardcoding transitions inside GUI widgets.

Keep automata definitions configurable so the group can change the organization-defined ID structure without rewriting the entire GUI.

### Testing requirements

Create pytest tests for:

- valid IDs
- invalid prefixes
- wrong lengths
- missing separators
- extra separators
- invalid symbols
- empty input
- boundary numeric values
- full acceptance/rejection behavior
- transition traces
- minimized DFA behavior

The tests should verify that the minimized DFA recognizes exactly the intended language.

### Documentation requirements

For every major module you implement, also provide a short Markdown explanation containing:

- purpose
- inputs
- outputs
- important classes/functions
- how it connects to Automata Theory
- how another team member can test it

Do not only generate code. The project is also being graded on understanding and documentation.

### Output format for implementation tasks

When implementing a feature, respond in this order:

1. What is being implemented.
2. Files to create/change.
3. Complete code for those files.
4. How to run it.
5. Tests to run.
6. Short explanation of how it connects to the automata theory.
7. Any assumptions made.

Never silently change the formal language definition. If the requested implementation conflicts with the agreed RE/NFA/DFA, explicitly identify the conflict before modifying the automata behavior.

### First implementation target

Start with the **Automata Core**, not the GUI.

Implement:

1. State/transition data models.
2. Employee ID language configuration.
3. Minimized DFA representation.
4. DFA simulation engine.
5. Structured simulation trace.
6. Unit tests.

After the core passes tests, implement the PySide6 GUI on top of the stable service layer.

---

# 24. Recommended Initial Team Sprint

To avoid blocking each other, start in parallel:

```text
Member 1 → Repository + project management
Member 2 → Formal language + examples
Member 3 → RE + NFA
Member 4 → DFA conversion
Member 5 → DFA minimization
Member 6 → Automata core framework
Member 7 → GUI wireframe / PySide6 shell
Member 8 → Test matrix + documentation structure
```

Once the formal automata design is stable, Member 6 connects the exact minimized DFA to the simulator, and Member 7 connects the simulator to the GUI.

This keeps the team moving in parallel while preventing the UI from becoming disconnected from the actual theory.

---

# 25. Final Principle

The project should not be presented as:

> "We made a form that checks whether an Employee ID looks correct."

It should be presented as:

> "We formally defined an Employee ID language, constructed its Regular Expression, NFA, DFA, and minimized DFA, then implemented the minimized DFA as an interactive Python simulator so the user can observe the recognition process symbol-by-symbol."

That framing directly connects the software to the requirements of Automata Theory and gives the group a strong basis for the live demonstration and defense.
