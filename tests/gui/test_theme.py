import re

import pytest

from app.gui.theme import PALETTE as P
from app.gui.theme import contrast, load_stylesheet

TEXT_PAIRS = [("text", "bg"), ("text", "surface"), ("muted", "bg"), ("muted", "surface"), ("muted", "surface2"),
              ("accent", "bg"), ("accent", "accent_bg"), ("accent_text", "accent"), ("ok", "ok_bg"),
              ("bad", "bad_bg"), ("ok", "bg"), ("bad", "bg")]
STROKE_PAIRS = [("line", "bg"), ("line", "surface"), ("accent", "bg"), ("bad", "bg"), ("ok", "bg")]


@pytest.mark.parametrize("fg, bg", TEXT_PAIRS)
def test_text_contrast_meets_wcag_aa(fg: str, bg: str) -> None:
    assert contrast(P[fg], P[bg]) >= 4.5


@pytest.mark.parametrize("fg, bg", STROKE_PAIRS)
def test_diagram_strokes_meet_graphics_contrast(fg: str, bg: str) -> None:
    assert contrast(P[fg], P[bg]) >= 3.0


def test_stylesheet_has_no_unresolved_tokens() -> None:
    assert not re.findall(r"@\w+@", load_stylesheet())
