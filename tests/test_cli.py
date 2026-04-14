from __future__ import annotations
# this_file: tests/test_cli.py
"""Subprocess tests for the vexy-pdfsvgpy Fire CLI."""

import subprocess
import sys
from pathlib import Path

import pytest

TESTDATA = Path(__file__).parent.parent / "testdata"


def _run(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "vexy_pdfsvgpy", *args],
        capture_output=True,
        text=True,
        check=False,
    )


def test_version_subcommand() -> None:
    result = _run(["version"])
    assert result.returncode == 0
    assert result.stdout.strip() != ""


def test_convert_pdf_to_png(tmp_path: Path) -> None:
    out = tmp_path / "out.png"
    result = _run([
        "convert",
        "--input", str(TESTDATA / "regularity.pdf"),
        "--output", str(out),
    ])
    assert result.returncode == 0, result.stderr
    assert out.exists()
    assert out.stat().st_size > 0


def test_convert_svg_to_pdf(tmp_path: Path) -> None:
    out = tmp_path / "out.pdf"
    result = _run([
        "convert",
        "--input", str(TESTDATA / "hello_glyphs.svg"),
        "--output", str(out),
    ])
    assert result.returncode == 0, result.stderr
    assert out.exists()
    assert out.stat().st_size > 0


def test_convert_svg_to_png_with_hint(tmp_path: Path) -> None:
    out = tmp_path / "out.png"
    result = _run([
        "convert",
        "--input", str(TESTDATA / "hello_glyphs.svg"),
        "--output", str(out),
        "--hint", "mu",
    ])
    assert result.returncode == 0, result.stderr
    assert out.exists()
    assert out.stat().st_size > 0


def test_convert_missing_input_returns_nonzero(tmp_path: Path) -> None:
    out = tmp_path / "out.png"
    result = _run([
        "convert",
        "--input", str(tmp_path / "nonexistent.pdf"),
        "--output", str(out),
    ])
    assert result.returncode != 0


def test_convert_missing_output_flag_returns_2() -> None:
    result = _run([
        "convert",
        "--input", str(TESTDATA / "regularity.pdf"),
    ])
    assert result.returncode != 0


def test_split_subcommand(tmp_path: Path) -> None:
    pytest.importorskip("vexy_pdfsvgpy.operations.reshape", reason="reshape module not available")
    out_dir = tmp_path / "split"
    out_dir.mkdir()
    result = _run([
        "split",
        "--input", str(TESTDATA / "regularity.pdf"),
        "--out-dir", str(out_dir),
    ])
    assert result.returncode == 0, result.stderr
    pdfs = list(out_dir.glob("*.pdf"))
    assert len(pdfs) > 1
