# System Architecture

```text
GUI (PySide6)            Simulate · Theory · Tests           app/gui/
   │  consumes structured results only — no automata logic
   ▼
Services                 SimulationService · ValidationService   app/services/
   │
   ▼
Automata core            regex → nfa → dfa → minimizer → simulator   app/core/
   │      pipeline.py derives everything once from ID_REGEX;
   │      present.py turns it into tables / diagram graphs / Markdown
   ▼
Data                     app/data/id_rules.py (ID_REGEX, Σ)   app/data/test_cases.py
```

## The pipeline

```text
ID_REGEX (formal RE)
   │ thompson()               ── ε-NFA        (26 states, 12 ε-edges)
   │ subset_construction()    ── DFA          (15 states incl. D_trap) + step log
   │ minimize()               ── minimal DFA  (q0…q13, q_trap) + refinement rounds
   ▼ dfa_equivalent()         ── product-automaton proof: DFA ≡ minimal DFA
Run engine (app/core/simulator.py) executes the minimal DFA symbol by symbol
```

The simulator never reads a hand-written table. `app/data/id_rules.py::REFERENCE_*` is a hand-written copy used
only to cross-check the derived DFA.

## Validation layers

1. **Layer 1 — alphabet:** the whole string is checked against Σ first; any symbol outside Σ rejects the input
   before the automaton runs (all offenders are listed).
2. **Layer 2 — automaton:** symbol-by-symbol run on the minimal DFA (or the subset DFA / ε-NFA for teaching).
3. **Layer 3 — presentation:** ACCEPTED / REJECTED, the reason, final state, symbols processed.

## One engine

`app.core.simulator.Run` is the only implementation of stepping, tracing and result-building.
`simulate()` loops over it and every `SimulationService` session wraps it, so the animated GUI and the
one-shot validator cannot disagree (tested for all three models over the whole suite).

## Modules

| Module | Responsibility |
|---|---|
| `core/regex.py` | RE AST + formal notation |
| `core/nfa.py` | ε-NFA, Thompson, ε-closure, move, subset construction |
| `core/dfa.py` | validated total DFA |
| `core/minimizer.py` | partition refinement with recorded rounds |
| `core/equivalence.py` | exact DFA equivalence + exhaustive agreement check |
| `core/pipeline.py` | RE → … → minimal DFA, cached |
| `core/simulator.py` | `Run`, `simulate`, `simulate_nfa` |
| `core/present.py` | grouped tables, diagram graphs, Markdown report |
| `services/` | facades for the GUI |
| `gui/` | theme, widgets (tape, verdict banner, model-driven diagram), pages |
