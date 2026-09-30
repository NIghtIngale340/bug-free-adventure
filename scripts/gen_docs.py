"""
Regenerate the tables embedded in docs/*.md from the code, so documentation cannot drift.

    python scripts/gen_docs.py            # rewrite the blocks
    python scripts/gen_docs.py --check    # exit 1 if any block is stale (used by the test-suite)

A block looks like  <!-- BEGIN generated:name --> ... <!-- END generated:name -->.
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from app.core.pipeline import get_pipeline  # noqa: E402
from app.core.present import (  # noqa: E402
    SUBSET_HEADERS,
    block_text,
    distance_rows,
    grouped_table,
    md_table,
    rounds_rows,
    subset_rows,
    tuple_lines,
)
from app.core.simulator import simulate  # noqa: E402
from app.data.test_cases import MASTER_TEST_SUITE  # noqa: E402

P = get_pipeline()


def _shown(s: str) -> str:
    return "(empty)" if s == "" else (repr(s) if s != s.strip() else s)


def _table(machine) -> str:
    t = grouped_table(machine)
    return md_table(t.headers, t.rows)


def _code(lines: list[str]) -> str:
    return "```text\n" + "\n".join(lines) + "\n```"


def _tests() -> str:
    rows = []
    for tc in MASTER_TEST_SUITE:
        r = simulate(tc.input_str)
        ok = r.accepted == tc.expected_accepted
        rows.append([tc.id, f"`{_shown(tc.input_str)}`", "Accepted" if tc.expected_accepted else "Rejected",
                     "Accepted" if r.accepted else "Rejected", "PASS" if ok else "FAIL", r.status.name])
    return md_table(["Test ID", "Input", "Expected", "Actual", "Pass/Fail", "Automaton outcome"], rows)


def _examples(accepted: bool) -> str:
    rows = [[f"`{_shown(t.input_str)}`", t.expected_reason] for t in MASTER_TEST_SUITE if t.expected_accepted == accepted]
    return md_table(["String", "Note" if accepted else "Reason rejected"], rows)


m = P.minimization
GENERATORS = {
    "regex-line": lambda: f"`{P.regex_formal}` = `{P.regex_expanded}`, where " + ", ".join(f"{k} = {v}" for k, v in P.regex_definitions.items()),
    "nfa-tuple": lambda: _code(tuple_lines("M_NFA", P.nfa)),
    "nfa-table": lambda: _table(P.nfa),
    "subset-table": lambda: md_table(SUBSET_HEADERS, subset_rows(P.subset_steps)),
    "dfa-tuple": lambda: _code(tuple_lines("M_DFA", P.subset_dfa)),
    "dfa-table": lambda: _table(P.subset_dfa),
    "min-rounds": lambda: md_table(["Round", "Blocks", "Partition"], rounds_rows(m)),
    "min-map": lambda: md_table(["Original", "Minimized", "Fewest symbols to accept"],
                                [[o, n, dict(distance_rows(m.dfa))[n]] for o, n in m.state_map.items()]),
    "min-tuple": lambda: _code(tuple_lines("M_min", m.dfa)),
    "min-table": lambda: _table(m.dfa),
    "min-summary": lambda: (
        f"States {m.states_before} → {m.states_after}; unreachable removed: {', '.join(m.removed_unreachable) or 'none'}; "
        f"merged groups: {', '.join(block_text(g) for g in m.merged_groups) or 'none (already minimal)'}; "
        f"partition refinement stabilised after {len(m.rounds) - 1} rounds."),
    "equiv-line": lambda: (
        f"Product-automaton check, subset DFA vs minimal DFA: **{'EQUAL' if P.equivalence.equal else 'DIFFERENT'}** "
        f"({P.equivalence.pairs_explored} state pairs explored)."),
    "accepted": lambda: _examples(True),
    "rejected": lambda: _examples(False),
    "test-table": _tests,
}

BLOCK = re.compile(r"(<!-- BEGIN generated:(\S+) -->\n)(.*?)(<!-- END generated:\2 -->)", re.S)


def render(text: str) -> str:
    return BLOCK.sub(lambda mt: f"{mt.group(1)}{GENERATORS[mt.group(2)]()}\n{mt.group(4)}", text)


def stale_files() -> list[Path]:
    return [p for p in sorted((ROOT / "docs").glob("*.md")) if render(p.read_text(encoding="utf-8")) != p.read_text(encoding="utf-8")]


if __name__ == "__main__":
    if "--check" in sys.argv:
        stale = stale_files()
        print("stale:", [p.name for p in stale] if stale else "none")
        sys.exit(1 if stale else 0)
    for path in sorted((ROOT / "docs").glob("*.md")):
        old = path.read_text(encoding="utf-8")
        new = render(old)
        if new != old:
            path.write_text(new, encoding="utf-8")
            print("updated", path.relative_to(ROOT))
