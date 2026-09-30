"""
STATEFUL SIMULATION SERVICE (step-by-step) over the derived automata

    create_session(input_string, mode) -> session_id
    step(session_id)                   -> TransitionStep | None
    run_all(session_id) / result(...)  -> SimulationResult
    reset(session_id) / close(...)
    get_metadata()                     -> AutomataMetadata
    get_pipeline()                     -> Pipeline  (NFA, subset steps, minimization rounds, ...)

Modes:  "DFA" minimal DFA (authoritative) · "SUBSET" DFA before minimization · "NFA" epsilon-NFA.
A session is a thin wrapper around app.core.simulator.Run, the same engine simulate() uses.
"""

from app.core.models import AutomataMetadata, SimulationResult, TransitionStep
from app.core.pipeline import Pipeline, get_pipeline
from app.core.simulator import Run, simulate

MODES = ("DFA", "SUBSET", "NFA")
_MAX_SESSIONS = 32


class SimulationService:
    def __init__(self) -> None:
        p = get_pipeline()
        self._pipeline = p
        self._machines = {"DFA": p.min_dfa, "SUBSET": p.subset_dfa, "NFA": p.nfa}
        self._sessions: dict[str, Run] = {}
        self._next_id = 0

    # --- sessions -------------------------------------------------------------

    def create_session(self, input_string: str, mode: str = "DFA") -> str:
        self._next_id += 1
        session_id = f"s{self._next_id}"
        self._sessions[session_id] = Run(input_string, self._machines[mode])
        while len(self._sessions) > _MAX_SESSIONS:
            self._sessions.pop(next(iter(self._sessions)))
        return session_id

    def close(self, session_id: str) -> None:
        self._sessions.pop(session_id, None)

    def reset(self, session_id: str) -> None:
        if run := self._sessions.get(session_id):
            run.reset()

    def step(self, session_id: str) -> TransitionStep | None:
        run = self._sessions.get(session_id)
        return run.step() if run else None

    def is_finished(self, session_id: str) -> bool:
        run = self._sessions.get(session_id)
        return run is None or run.finished

    def active_states(self, session_id: str) -> frozenset[str]:
        """Automaton states the run is currently in (a set: one for a DFA, several for the NFA)."""
        run = self._sessions.get(session_id)
        return run.active if run else frozenset()

    def run_all(self, session_id: str) -> SimulationResult:
        """Finish the remaining symbols and return the final result."""
        run = self._sessions.get(session_id)
        return run.result() if run else simulate("")

    result = run_all

    # --- one-shot ---------------------------------------------------------------

    def validate(self, input_string: str, mode: str = "DFA") -> SimulationResult:
        return simulate(input_string, self._machines[mode])

    # --- theory data --------------------------------------------------------------

    def get_pipeline(self) -> Pipeline:
        return self._pipeline

    def get_metadata(self) -> AutomataMetadata:
        p, m = self._pipeline, self._pipeline.minimization
        merged = [list(g) for g in m.merged_groups]
        note = (
            f"Moore partition refinement stabilised after {len(m.rounds) - 1} rounds. "
            + (f"{len(merged)} group(s) of equivalent states were merged."
               if merged else
               f"No states were merged: all {m.states_after} states are pairwise distinguishable "
               "(each needs a different number of further symbols to reach acceptance).")
        )
        return AutomataMetadata(
            states=list(m.dfa.states),
            alphabet=sorted(m.dfa.alphabet),
            start_state=m.dfa.start_state,
            accepting_states=sorted(m.dfa.accepting_states),
            transition_table=m.dfa.transition_table(),
            re_pattern=p.regex_formal,
            minimization_summary={
                "unminimized_states": m.states_before,
                "minimized_states": m.states_after,
                "states_before": m.states_before,
                "states_after": m.states_after,
                "unreachable_removed": list(m.removed_unreachable),
                "rounds": len(m.rounds) - 1,
                "merged_groups": merged,
                "note": note,
                "minimized": True,
            },
            nfa_summary={
                "states": list(p.nfa.states),
                "alphabet": sorted(p.nfa.alphabet),
                "start_state": p.nfa.start_state,
                "accepting_states": sorted(p.nfa.accepting_states),
                "epsilon_edges": p.nfa.epsilon_edge_count,
                "subset_trace": [(s.name, sorted(s.subset)) for s in p.subset_steps if s.subset],
                "note": ("Thompson ε-NFA built from the regular expression; subset construction "
                         f"produced {len(p.subset_dfa.states)} DFA states (including the dead state)."),
            },
        )
