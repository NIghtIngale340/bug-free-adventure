"""Documentation must match the code: embedded tables are generated, assets exist."""

from pathlib import Path

from scripts import gen_docs

ROOT = Path(__file__).resolve().parent.parent


def test_generated_doc_tables_are_current() -> None:
    assert [p.name for p in gen_docs.stale_files()] == [], "run: python scripts/gen_docs.py"


def test_every_generated_block_has_a_generator() -> None:
    for path in (ROOT / "docs").glob("*.md"):
        for name in gen_docs.BLOCK.findall(path.read_text(encoding="utf-8")):
            assert name[1] in gen_docs.GENERATORS


def test_diagram_and_screenshot_assets_exist() -> None:
    for name in ("nfa.png", "dfa_subset_construction.png", "dfa_minimal.png"):
        assert (ROOT / "assets" / "diagrams" / name).stat().st_size > 5_000
    assert len(list((ROOT / "assets" / "screenshots").glob("*.png"))) >= 8


def test_docs_do_not_claim_removed_things() -> None:
    text = "\n".join(p.read_text(encoding="utf-8") for p in (ROOT / "docs").glob("*.md"))
    assert "unminimized_states: 18" not in text and "--mock" not in text and "test_e2e_pipeline" not in text
    for md in [*(ROOT / "docs").rglob("*.md"), ROOT / "README.md", ROOT / "TEAM_DEVELOPMENT_GUIDE.md"]:
        for target in __import__("re").findall(r"\]\(((?!http|mailto|#)[^)#]+)\)", md.read_text(encoding="utf-8")):
            assert (md.parent / target).exists(), f"{md.name}: broken link {target}"


def test_team_guide_describes_the_current_repo() -> None:
    text = (ROOT / "TEAM_DEVELOPMENT_GUIDE.md").read_text(encoding="utf-8")
    assert "scripts/gen_docs.py" in text and "MockAutomataService" not in text and "file://" not in text
