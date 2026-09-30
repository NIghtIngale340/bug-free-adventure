"""
ONE PALETTE for the stylesheet (styles/theme.qss uses @token@ placeholders) and for the
painted widgets (diagram, tape). Contrast targets (WCAG 2.1): text >= 4.5:1, strokes >= 3:1
against their background; tests/gui/test_theme.py enforces them.
"""

from pathlib import Path

PALETTE = {
    "bg": "#0E1116", "surface": "#161B22", "surface2": "#1E2530", "border": "#2E3846",
    "line": "#8794AA",                                   # diagram strokes / arrows
    "text": "#E8ECF2", "muted": "#A3AEC0",
    "accent": "#F2B84B", "accent_hover": "#F8CB70", "accent_text": "#1A1305", "accent_bg": "#3A2F14",
    "ok": "#4BDCA0", "ok_bg": "#0F2B22",
    "bad": "#FF8A8A", "bad_bg": "#341A1F",
    "info": "#86B8FF", "seg_a": "#86B8FF", "seg_b": "#C3A6FF",   # alternating RE-segment colours
}
FONT_UI = '"Inter", "Segoe UI", "Noto Sans", "DejaVu Sans", sans-serif'
FONT_MONO = '"JetBrains Mono", "Consolas", "DejaVu Sans Mono", monospace'

_QSS = Path(__file__).parent / "styles" / "theme.qss"
_FONTS = Path(__file__).parent / "fonts"


def load_fonts() -> list[str]:
    """Register any .ttf/.otf dropped into app/gui/fonts/ (see the README there); returns the families."""
    from PySide6.QtGui import QFontDatabase
    families: list[str] = []
    for f in sorted([*_FONTS.glob("*.ttf"), *_FONTS.glob("*.otf")]):
        fid = QFontDatabase.addApplicationFont(str(f))
        if fid >= 0:
            families += QFontDatabase.applicationFontFamilies(fid)
    return families


def load_stylesheet() -> str:
    """theme.qss with @tokens@ replaced. The path is relative to this file, not the cwd."""
    css = _QSS.read_text(encoding="utf-8")
    for key, value in {**PALETTE, "font_ui": FONT_UI, "font_mono": FONT_MONO}.items():
        css = css.replace(f"@{key}@", value)
    return css


def contrast(fg: str, bg: str) -> float:
    def lum(h: str) -> float:
        rgb = [int(h.lstrip("#")[i:i + 2], 16) / 255 for i in (0, 2, 4)]
        lin = [c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4 for c in rgb]
        return 0.2126 * lin[0] + 0.7152 * lin[1] + 0.0722 * lin[2]
    hi, lo = sorted((lum(fg), lum(bg)), reverse=True)
    return (hi + 0.05) / (lo + 0.05)
