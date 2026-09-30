import pytest

from app.core.pipeline import get_pipeline


@pytest.fixture(scope="session")
def pipeline():
    return get_pipeline()


@pytest.fixture(scope="session")
def dfa(pipeline):
    """The derived minimal DFA, i.e. the recognizer the simulator runs."""
    return pipeline.min_dfa
