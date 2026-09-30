"""RE == NFA == DFA == minimal DFA: exact proof + oracle-backed sampling."""

import copy
import itertools
import random
import re

import pytest

from app.core.dfa import DFA
from app.core.equivalence import dfa_equivalent
from app.core.pipeline import reference_dfa
from app.core.simulator import simulate, simulate_nfa
from app.data.id_rules import ALPHABET, RE_PATTERN

ORACLE = re.compile(RE_PATTERN)          # fullmatch semantics: '$' would accept a trailing newline
SIGMA = sorted(ALPHABET)
EXTRA = list("abcxyzemp _!@#\t\n") + ["٣", "０", "É", "​", "‐", "–", "Е"]


def test_exact_equivalence_of_the_pipeline_stages(pipeline) -> None:
    assert pipeline.equivalence.equal and pipeline.equivalence.pairs_explored == 15
    assert dfa_equivalent(pipeline.subset_dfa, pipeline.min_dfa).equal


def test_derived_dfa_equals_hand_written_reference(pipeline) -> None:
    assert dfa_equivalent(pipeline.min_dfa, reference_dfa()).equal
    assert pipeline.min_dfa.transition_table() == reference_dfa().transition_table()


@pytest.mark.parametrize("state, symbol, target", [
    ("q7", "-", "q9"),        # 3-digit years accepted
    ("q13", "0", "q13"),      # unbounded sequence number (rare: random fuzzing barely sees it)
    ("q3", "0", "q5"),        # first hyphen optional
    ("q12", "9", "q_trap"),
])
def test_equivalence_check_catches_a_single_wrong_transition(pipeline, state, symbol, target) -> None:
    t = copy.deepcopy(pipeline.min_dfa.transition_table())
    t[state][symbol] = target
    mutant = DFA(pipeline.min_dfa.states, pipeline.min_dfa.alphabet, t, "q0", {"q13"})
    result = dfa_equivalent(pipeline.min_dfa, mutant)
    assert not result.equal
    assert pipeline.min_dfa.accepts(result.counterexample) != mutant.accepts(result.counterexample)


def _every_model(w: str, pipeline) -> dict[str, bool]:
    return {
        "min_dfa": pipeline.min_dfa.accepts(w), "subset_dfa": pipeline.subset_dfa.accepts(w),
        "nfa": pipeline.nfa.accepts(w), "simulate": simulate(w).accepted,
        "simulate_nfa": simulate_nfa(w).accepted, "simulate_subset": simulate(w, pipeline.subset_dfa).accepted,
    }


def _check(words, pipeline) -> None:
    for w in words:
        truth = ORACLE.fullmatch(w) is not None
        wrong = {k for k, v in _every_model(w, pipeline).items() if v != truth}
        assert not wrong, f"{w!r}: oracle says {truth}, disagree: {wrong}"


def test_exhaustive_all_words_up_to_length_4(pipeline) -> None:
    _check((("".join(t)) for n in range(5) for t in itertools.product(SIGMA, repeat=n)), pipeline)


def test_neighbourhood_of_valid_ids(pipeline) -> None:
    rng = random.Random(7)
    words = []
    for _ in range(40):
        base = f"EMP-{rng.randrange(10**4):04d}-{rng.randrange(10**4):04d}"
        words += [base[:i] + base[i + 1:] for i in range(len(base))]                       # deletions
        words += [base[:i] + c + base[i:] for i in range(len(base) + 1) for c in "E-0Z "]   # insertions
        words += [base[:i] + c + base[i + 1:] for i in range(len(base)) for c in "E-9Oo "]  # substitutions
    _check(words, pipeline)


def test_random_words_including_unicode_lookalikes(pipeline) -> None:
    rng = random.Random(2026)

    def gen() -> str:
        r = rng.random()
        base = f"EMP-{rng.randrange(10**4):04d}-{rng.randrange(10**4):04d}"
        if r < .3:
            return base
        if r < .7:
            chars = list(base)
            for _ in range(rng.randint(1, 3)):
                chars[rng.randrange(len(chars))] = rng.choice(SIGMA + EXTRA)
            return "".join(chars)
        return "".join(rng.choice(SIGMA + EXTRA) for _ in range(rng.randint(0, 20)))

    _check((gen() for _ in range(20_000)), pipeline)


@pytest.mark.parametrize("w, why", [
    ("EMP-2026-0001\n", "'$' would accept this; L does not"),
    ("EMP-2026-000１", "full-width digit"),
    ("EMP-2026-٠٠٠١", "Arabic-Indic digits (str.isdigit trap)"),
    ("EMP-2O26-0001", "letter O for zero"),
    ("EMP-2026‐0001", "U+2010 hyphen"),
    ("ЕMP-2026-0001", "Cyrillic Е"),
])
def test_lookalike_words_are_rejected_everywhere(pipeline, w: str, why: str) -> None:
    assert not any(_every_model(w, pipeline).values()), why


def test_every_single_transition_mutation_is_detected(pipeline) -> None:
    """The minimal DFA has no equivalent states, so redirecting ANY one transition changes L
    (2,940 mutants) and the exact check must always return a distinguishing word."""
    d, table = pipeline.min_dfa, pipeline.min_dfa.transition_table()
    for state in d.states:
        for symbol in d.alphabet:
            for target in d.states:
                if target == table[state][symbol]:
                    continue
                mutated = copy.deepcopy(table)
                mutated[state][symbol] = target
                m = DFA(d.states, d.alphabet, mutated, "q0", {"q13"})
                r = dfa_equivalent(d, m)
                assert not r.equal and d.accepts(r.counterexample) != m.accepts(r.counterexample), (state, symbol, target)
