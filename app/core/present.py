"""
PRESENTATION DATA derived from core objects (pure Python, no Qt)

Grouped transition tables, diagram graphs and the Markdown report. Used by the GUI,
by the docs generator (scripts/gen_docs.py) and by the tests, so what is shown is
always what is executed.
"""

from dataclasses import dataclass

from app.core.dfa import DFA, natural_key
from app.core.language import describe_symbols
from app.core.minimizer import MinimizationResult
from app.core.nfa import NFA, SubsetStep
from app.core.pipeline import Pipeline
from app.core.simulator import format_subset
from app.data.id_rules import DIGITS

# --- symbol helpers -------------------------------------------------------------


def _sym_key(c: str) -> tuple:
    return (0 if c.isalpha() else 1 if c == "-" else 2, c)


def compress_symbols(symbols) -> str:
    """{'0'..'9','-'} -> '-, 0–9' ; a full digit set collapses to '0–9'."""
    syms = set(symbols)
    full = set(DIGITS) <= syms
    parts = [c for c in sorted(syms, key=_sym_key) if not (full and c in DIGITS)]
    return ", ".join(parts + (["0–9"] if full else []))


def block_text(block, limit: int = 4) -> str:
    b = list(block)
    return "{" + ", ".join(b) + "}" if len(b) <= limit else f"{{{b[0]}, {b[1]}, …, {b[-1]}}} ({len(b)})"


# --- grouped transition tables ------------------------------------------------------


@dataclass(frozen=True)
class Table:
    headers: list[str]
    rows: list[list[str]]
    col_of: dict[str, int]      # symbol -> column index (for highlighting a used transition)


def grouped_table(machine: DFA | NFA) -> Table:
    """
    Table of the transition function with identical symbol columns merged
    (e.g. one '0–9' column instead of ten). DFA cells are always filled: undefined
    moves show the dead state, so delta is visibly total. NFA cells show sets; ε is a column.
    """
    is_nfa = isinstance(machine, NFA)
    states = machine.states
    if is_nfa:
        cell = lambda s, a: format_subset(machine.transitions[s].get(a, ()))   # noqa: E731
        blank = {"∅"}
    else:
        cell = lambda s, a: machine.transitions[s][a]   # noqa: E731
        blank = set(machine.dead_states)

    groups: dict[tuple, list[str]] = {}
    for a in sorted(machine.alphabet):
        groups.setdefault(tuple(cell(s, a) for s in states), []).append(a)

    def first_use(col: tuple) -> int:
        return next((i for i, v in enumerate(col) if v not in blank), len(col))

    cols = sorted(groups.items(), key=lambda kv: (first_use(kv[0]), _sym_key(kv[1][0])))
    headers = ["State"] + [compress_symbols(g) for _, g in cols]
    rows = []
    for i, s in enumerate(states):
        label = ("→ " if s == machine.start_state else "") + s + (" *" if s in machine.accepting_states else "")
        row = [label] + [col[i] for col, _ in cols]
        if is_nfa:
            row.append(format_subset(machine.epsilon[s]))
        rows.append(row)
    if is_nfa:
        headers.append("ε")
    col_of = {a: j + 1 for j, (_, g) in enumerate(cols) for a in g}
    return Table(headers, rows, col_of)


# --- diagram graphs -------------------------------------------------------------------


@dataclass(frozen=True)
class GNode:
    name: str
    caption: str = ""
    start: bool = False
    accepting: bool = False
    dead: bool = False
    tip: str = ""          # explanation shown on hover / click


@dataclass(frozen=True)
class GEdge:
    src: str
    dst: str
    label: str
    symbols: frozenset[str]
    epsilon: bool = False
    tip: str = ""


@dataclass(frozen=True)
class Graph:
    title: str
    nodes: tuple[GNode, ...]
    edges: tuple[GEdge, ...]


def _dfa_tip(dfa: DFA, s: str, caption: str) -> str:
    if dfa.is_dead(s):
        return (f"{s} — dead state: no accepting state can be reached from here, so a run that enters it is "
                "rejected. Every undefined (state, symbol) move ends here.")
    role = " (start state q₀)" if s == dfa.start_state else " (accepting state, in F)" if dfa.is_accepting(s) else ""
    text = f"{s}{role}"
    if caption:
        text += f" stands for the NFA subset {caption}"
    exp = dfa.expected(s)
    text += (". Input ending here is ACCEPTED." if dfa.is_accepting(s) and not exp else
             f". Expects {describe_symbols(exp)} next; at least {dfa.symbols_needed(s)} more symbol(s) needed to accept.")
    return text


def dfa_graph(dfa: DFA, title: str, captions: dict[str, str] | None = None) -> Graph:
    """Edges into dead states are omitted (drawn as one 'else -> dead' note by the widget)."""
    captions = captions or {}
    live = [s for s in dfa.states if s not in dfa.dead_states]
    nodes = tuple(GNode(s, captions.get(s, ""), s == dfa.start_state, dfa.is_accepting(s),
                        tip=_dfa_tip(dfa, s, captions.get(s, ""))) for s in live)
    nodes += tuple(GNode(s, captions.get(s, ""), dead=True, tip=_dfa_tip(dfa, s, "")) for s in dfa.states if dfa.is_dead(s))
    pairs: dict[tuple[str, str], set[str]] = {}
    for s in live:
        for a, t in dfa.transitions[s].items():
            if t not in dfa.dead_states:
                pairs.setdefault((s, t), set()).add(a)
    edges = tuple(GEdge(u, v, compress_symbols(sy), frozenset(sy),
                        tip=f"δ({u}, {compress_symbols(sy)}) = {v} — reading {compress_symbols(sy)} in {u} moves to {v}.")
                  for (u, v), sy in pairs.items())
    return Graph(title, nodes, edges)


def nfa_graph(nfa: NFA, title: str) -> Graph:
    def node_tip(s: str) -> str:
        role = " (start state)" if s == nfa.start_state else " (accepting state)" if s in nfa.accepting_states else ""
        moves = nfa.expected([s])
        parts = ([f"reads {describe_symbols(moves)}"] if moves else []) + \
                ([f"ε-moves to {format_subset(nfa.epsilon[s])}"] if nfa.epsilon[s] else [])
        need = nfa.symbols_needed([s])
        return (f"{s}{role}: " + (" and ".join(parts) if parts else "no outgoing moves")
                + (f". At least {need} more symbol(s) needed to accept." if need else "."))

    nodes = tuple(GNode(s, start=s == nfa.start_state, accepting=s in nfa.accepting_states, tip=node_tip(s))
                  for s in nfa.states)
    edges: list[GEdge] = []
    for s in nfa.states:
        pairs: dict[str, set[str]] = {}
        for a, ts in nfa.transitions[s].items():
            for t in ts:
                pairs.setdefault(t, set()).add(a)
        edges += [GEdge(s, t, compress_symbols(sy), frozenset(sy),
                        tip=f"δ({s}, {compress_symbols(sy)}) ∋ {t} — reading {compress_symbols(sy)} in {s} can move to {t}.")
                  for t, sy in pairs.items()]
        edges += [GEdge(s, t, "ε", frozenset(), epsilon=True,
                        tip=f"ε-move {s} → {t}: no input is read. ε-closure follows these edges, so {t} is active whenever {s} is.")
                  for t in sorted(nfa.epsilon[s])]
    return Graph(title, nodes, tuple(edges))


def pipeline_graphs(p: Pipeline) -> dict[str, Graph]:
    """The three automata of the pipeline, keyed by simulator mode."""
    caps = {s.name: format_subset(s.subset) for s in p.subset_steps if s.subset}
    return {
        "NFA": nfa_graph(p.nfa, "ε-NFA (Thompson construction from the RE)"),
        "SUBSET": dfa_graph(p.subset_dfa, "DFA (subset construction, not yet minimized)", caps),
        "DFA": dfa_graph(p.min_dfa, "Minimal DFA (authoritative recognizer)"),
    }


# --- Markdown -------------------------------------------------------------------------


def md_table(headers: list[str], rows: list[list[str]]) -> str:
    esc = lambda x: str(x).replace("|", "\\|")   # noqa: E731
    lines = ["| " + " | ".join(esc(h) for h in headers) + " |", "|" + "|".join("---" for _ in headers) + "|"]
    lines += ["| " + " | ".join(esc(c) for c in r) + " |" for r in rows]
    return "\n".join(lines)


def _hr(t: Table) -> tuple[list[str], list[list[str]]]:
    return t.headers, t.rows


def subset_rows(steps: list[SubsetStep]) -> list[list[str]]:
    rows = []
    for st in steps:
        first = True
        for m in st.moves:
            rows.append([
                (st.name + (" *" if st.accepting else "")) if first else "",
                format_subset(st.subset) if first else "",
                compress_symbols(m.symbols), format_subset(m.move), format_subset(m.closure), m.target,
            ])
            first = False
    return rows


SUBSET_HEADERS = ["DFA state", "NFA subset", "Symbols a", "move(S, a)", "ε-closure", "Target"]


def rounds_rows(res: MinimizationResult) -> list[list[str]]:
    return [[f"P{k}", str(len(part)), "  ".join(block_text(b) for b in part)]
            for k, part in enumerate(res.rounds)]


def distance_rows(dfa: DFA) -> list[list[str]]:
    return [[s, str(d) if (d := dfa.symbols_needed(s)) is not None else "∞ (dead)"] for s in dfa.states]


def tuple_lines(name: str, machine: DFA | NFA) -> list[str]:
    q = machine.states
    qtxt = ", ".join(q) if len(q) <= 16 else f"{q[0]}, {q[1]}, …, {q[-1]}"
    return [f"{name} = (Q, Σ, δ, q₀, F)",
            f"Q  = {{{qtxt}}}   ({len(q)} states)",
            f"Σ  = {{{', '.join(sorted(machine.alphabet, key=_sym_key))}}}   ({len(machine.alphabet)} symbols)",
            f"q₀ = {machine.start_state}",
            f"F  = {{{', '.join(sorted(machine.accepting_states, key=natural_key))}}}"]


def report_md(p: Pipeline, result=None) -> str:
    m = p.minimization
    out = [
        "# Automata Theory Report — Employee ID Validator", "",
        "**Course:** CCAUTOMA — 1st AY 2026", "",
        "**Pipeline:** RE → ε-NFA (Thompson) → DFA (subset construction) → minimal DFA (Moore partition refinement)", "",
        f"**Regular expression:** `{p.regex_formal}`  =  `{p.regex_expanded}`, "
        + ", ".join(f"{k} = {v}" for k, v in p.regex_definitions.items()), "",
        "## ε-NFA", "```", *tuple_lines("M_NFA", p.nfa), "```",
        md_table(*_hr(grouped_table(p.nfa))), "",
        "## Subset construction", md_table(SUBSET_HEADERS, subset_rows(p.subset_steps)), "",
        "## DFA (before minimization)", "```", *tuple_lines("M_DFA", p.subset_dfa), "```",
        md_table(*_hr(grouped_table(p.subset_dfa))), "",
        "## Minimization",
        f"Unreachable states removed: {', '.join(m.removed_unreachable) or 'none'}.  "
        f"States {m.states_before} → {m.states_after}; merged groups: "
        f"{', '.join(block_text(g) for g in m.merged_groups) or 'none (already minimal)'}.", "",
        md_table(["Round", "Blocks", "Partition"], rounds_rows(m)), "",
        md_table(["State", "Fewest symbols to accept"], distance_rows(m.dfa)), "",
        "## Minimal DFA", "```", *tuple_lines("M_min", m.dfa), "```",
        md_table(*_hr(grouped_table(m.dfa))), "",
        f"**Equivalence (product automaton, subset DFA vs minimal DFA):** "
        f"{'EQUAL' if p.equivalence.equal else 'DIFFERENT'} — {p.equivalence.pairs_explored} state pairs explored.",
    ]
    if result is not None:
        out += ["", f"## Evaluation of `{result.input_string}`",
                f"- **Verdict:** {'ACCEPTED' if result.accepted else 'REJECTED'} (`{result.status.name}`)",
                f"- **Final state:** `{result.final_state or '—'}`",
                f"- **Symbols processed:** {result.processed_symbols} / {result.total_symbols}",
                f"- **Explanation:** {result.explanation}", ""]
        if result.trace:
            out.append(md_table(["Step", "Symbol", "From", "To", "Valid", "Explanation"],
                                [[t.step, t.symbol, t.from_state, t.to_state, "yes" if t.is_valid else "no",
                                  t.explanation] for t in result.trace]))
    return "\n".join(out) + "\n"
