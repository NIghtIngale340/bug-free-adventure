# Employee ID Validator — CCAUTOMA

An Automata Theory project that recognizes organization-defined employee IDs (`EMP-YYYY-NNNN`) and makes the
whole pipeline visible:

```text
Formal language → Regular expression → ε-NFA → subset construction → DFA → minimization → minimal DFA → simulator
```

Nothing is hand-typed: the NFA is built from the regular expression (Thompson), the DFA from the NFA
(subset construction), the minimal DFA from the DFA (partition refinement), and the simulator runs the minimal DFA.
The GUI has three views: **Simulate** (step through an ID symbol by symbol on the DFA, the pre-minimization DFA or the ε-NFA),
**Theory** (every stage with tables and diagrams, generated from the same objects) and **Tests** (28-case suite + batch input).

## Run

```bash
python3 -m venv .venv && source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python -m app.main            # the application
python -m pytest              # 250+ tests (GUI tests run offscreen)
python scripts/gen_docs.py    # regenerate the tables embedded in docs/ (add --check to verify)
python scripts/export_assets.py   # diagrams + screenshots into assets/
```

Simulate shortcuts: **Space** play/pause (or activates the focused button) · **→** step · **←** previous step · **Ctrl+R** reset.
Hover or click any state or transition in a diagram for an explanation; coloured bars under the tape show which part of the
regular expression matches each symbol. Set `CAUTOMA_REDUCE_MOTION=1` to disable the 180 ms state transitions.
Optional fonts (Inter, JetBrains Mono): see [app/gui/fonts/README.md](app/gui/fonts/README.md).

## Documentation

| | |
|---|---|
| [docs/formal_language.md](docs/formal_language.md) | problem, Σ, L, examples |
| [docs/regex.md](docs/regex.md) | formal RE and components |
| [docs/nfa.md](docs/nfa.md) | ε-NFA (Thompson), table, diagram |
| [docs/dfa.md](docs/dfa.md) | subset construction trace, DFA table, diagram |
| [docs/minimization.md](docs/minimization.md) | refinement rounds, no-merge proof, equivalence |
| [docs/architecture.md](docs/architecture.md) | layers, pipeline, modules |
| [docs/testing.md](docs/testing.md) | strategy and suite results |
| [docs/DEFENSE_SCRIPT_AND_QA.md](docs/DEFENSE_SCRIPT_AND_QA.md) | demo script and Q&A bank |
| [TEAM_DEVELOPMENT_GUIDE.md](TEAM_DEVELOPMENT_GUIDE.md) | team workflow (planning docs in `docs/internal/`) |
