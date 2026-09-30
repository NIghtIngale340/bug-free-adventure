"""
THE PIPELINE:  RE -> epsilon-NFA -> DFA (subset construction) -> minimal DFA

Everything the simulator and the GUI show is derived here, once, from ID_REGEX.
get_pipeline() is cached; the objects it returns must be treated as read-only.
"""

from dataclasses import dataclass
from functools import lru_cache

from app.core.dfa import DFA
from app.core.equivalence import Equivalence, dfa_equivalent
from app.core.minimizer import MinimizationResult, minimize
from app.core.nfa import NFA, SubsetStep, subset_construction, thompson
from app.core.regex import Node, definitions, expanded, formal
from app.data.id_rules import (
    ID_REGEX,
    REFERENCE_ACCEPTING,
    REFERENCE_START,
    REFERENCE_STATES,
    REFERENCE_TRANSITIONS,
    TRAP_STATE,
)


@dataclass(frozen=True)
class Pipeline:
    regex: Node
    regex_formal: str
    regex_expanded: str
    regex_definitions: dict[str, str]
    nfa: NFA
    subset_dfa: DFA
    subset_steps: list[SubsetStep]
    minimization: MinimizationResult
    equivalence: Equivalence          # subset DFA  vs  minimal DFA

    @property
    def min_dfa(self) -> DFA:
        return self.minimization.dfa


def build_pipeline(regex: Node = ID_REGEX) -> Pipeline:
    nfa = thompson(regex)
    subset_dfa, steps = subset_construction(nfa)
    minimization = minimize(subset_dfa)
    return Pipeline(
        regex, formal(regex), expanded(regex), definitions(regex),
        nfa, subset_dfa, steps, minimization,
        dfa_equivalent(subset_dfa, minimization.dfa),
    )


@lru_cache(maxsize=1)
def get_pipeline() -> Pipeline:
    return build_pipeline()


def reference_dfa() -> DFA:
    """The hand-written automaton from id_rules, for cross-checking only."""
    return DFA(REFERENCE_STATES, get_pipeline().min_dfa.alphabet,
               {s: {a: REFERENCE_TRANSITIONS[s].get(a, TRAP_STATE) for a in get_pipeline().min_dfa.alphabet}
                for s in REFERENCE_STATES},
               REFERENCE_START, REFERENCE_ACCEPTING)
