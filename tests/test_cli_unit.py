"""In-process unit tests for the Fire CLI class.

The subprocess tests in ``test_cli.py`` prove the wired-up command works
end to end; these call the same ``CLI`` methods directly so coverage sees them
and each branch (success, bad input, missing args) is checked in isolation.
"""

# this_file: tests/test_cli_unit.py
from __future__ import annotations

from pathlib import Path

from vexy_pdfsvgpy.cli import CLI

TESTDATA = Path(__file__).parent / "fixtures"


def test_version_returns_string() -> None:
    assert CLI().version().strip() != ""


def test_convert_pdf_to_png_returns_zero(tmp_path: Path) -> None:
    out = tmp_path / "out.png"
    rc = CLI().convert(input=str(TESTDATA / "regularity.pdf"), output=str(out))
    assert rc == 0
    assert out.exists() and out.stat().st_size > 0


def test_convert_svg_to_pdf_returns_zero(tmp_path: Path) -> None:
    out = tmp_path / "out.pdf"
    rc = CLI().convert(input=str(TESTDATA / "hello_glyphs.svg"), output=str(out))
    assert rc == 0
    assert out.read_bytes()[:4] == b"%PDF"


def test_convert_missing_args_returns_2() -> None:
    assert CLI().convert(input=None, output=None) == 2


def test_convert_bad_input_returns_1(tmp_path: Path) -> None:
    rc = CLI().convert(input=str(tmp_path / "nope.pdf"), output=str(tmp_path / "o.png"))
    assert rc == 1


def test_regularize_shortcut(tmp_path: Path) -> None:
    out = tmp_path / "reg.pdf"
    rc = CLI().regularize(input=str(TESTDATA / "papercut.pdf"), output=str(out))
    assert rc == 0
    assert out.exists()


def test_split_and_merge_round_trip(tmp_path: Path) -> None:
    cli = CLI()
    split_dir = tmp_path / "split"
    split_dir.mkdir()
    assert cli.split(input=str(TESTDATA / "regularity.pdf"), out_dir=str(split_dir)) == 0
    pages = sorted(split_dir.glob("*.pdf"))
    assert len(pages) > 1
    merged = tmp_path / "merged.pdf"
    assert cli.merge(inputs=",".join(str(p) for p in pages), output=str(merged)) == 0
    assert merged.read_bytes()[:4] == b"%PDF"


def test_merge_empty_input_returns_1(tmp_path: Path) -> None:
    assert CLI().merge(inputs="", output=str(tmp_path / "x.pdf")) == 1


def test_split_bad_input_returns_1(tmp_path: Path) -> None:
    assert CLI().split(input=str(tmp_path / "missing.pdf"), out_dir=str(tmp_path)) == 1


def test_format_shortcut_method(tmp_path: Path) -> None:
    # _register_format_shortcuts() attached per-format methods like pdf_s.
    cli = CLI()
    assert hasattr(cli, "png_s")
    out = tmp_path / "shortcut.png"
    rc = cli.png_s(input=str(TESTDATA / "hello_glyphs.svg"), output=str(out))
    assert rc == 0
    assert out.read_bytes()[:8] == b"\x89PNG\r\n\x1a\n"
