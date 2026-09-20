"""Unit tests for BE-001: formal language & alphabet validator."""

import pytest

from app.core.language import (
    describe_language,
    is_symbol_in_alphabet,
    validate_symbols,
)
from app.data.id_rules import ALPHABET


# --- is_symbol_in_alphabet --------------------------------------------------

@pytest.mark.parametrize("ch", ["E", "M", "P", "-", "0", "5", "9"])
def test_symbols_inside_alphabet(ch: str) -> None:
    assert is_symbol_in_alphabet(ch) is True


@pytest.mark.parametrize("ch", ["e", "A", "!", " ", "_", "10", ""])
def test_symbols_outside_alphabet(ch: str) -> None:
    assert is_symbol_in_alphabet(ch) is False


def test_alphabet_size_is_14() -> None:
    assert len(ALPHABET) == 14


# --- validate_symbols -------------------------------------------------------

def test_validate_symbols_all_legal() -> None:
    ok, errors = validate_symbols("EMP-2026-0042")
    assert ok is True
    assert errors == []


def test_validate_symbols_reports_positions() -> None:
    ok, errors = validate_symbols("EMP-2026-12A4!")
    assert ok is False
    # 'A' at index 11, '!' at index 13
    assert errors == [(11, "A"), (13, "!")]


def test_validate_symbols_empty_string_is_ok() -> None:
    # Empty input is legal at the alphabet layer; rejection happens in simulator.
    ok, errors = validate_symbols("")
    assert ok is True
    assert errors == []


def test_validate_symbols_lowercase_prefix() -> None:
    ok, errors = validate_symbols("emp-2026-0001")
    assert ok is False
    assert errors == [(0, "e"), (1, "m"), (2, "p")]


# --- describe_language ------------------------------------------------------

def test_describe_language_contains_core_facts() -> None:
    info = describe_language()
    assert info["format"] == "EMP-YYYY-NNNN"
    assert info["total_length"] == 13
    assert info["alphabet_size"] == 14
    assert "E" in info["alphabet"] and "9" in info["alphabet"]