from __future__ import annotations
# this_file: tests/test_pipeline.py
"""Tests for pipeline.py — plan() and execute()."""

from pathlib import Path

import pytest

from vexy_pdfsvgpy.dispatch import Capability
from vexy_pdfsvgpy.errors import BackendFailure, UnsupportedConversion
from vexy_pdfsvgpy.pipeline import execute, plan
from vexy_pdfsvgpy.types import FormatSpec

TESTDATA = Path(__file__).parent.parent / "testdata"


def test_plan_pdf_to_png() -> None:
    steps = plan(FormatSpec.parse("pdf"), FormatSpec.parse("png"))
    assert len(steps) == 1
    assert steps[0].capability == Capability.PDF_TO_PNG


def test_plan_svg_to_pdf() -> None:
    steps = plan(FormatSpec.parse("svg"), FormatSpec.parse("pdf"))
    assert len(steps) == 1
    assert steps[0].capability == Capability.SVG_TO_PDF


def test_plan_pdf_normalize() -> None:
    steps = plan(FormatSpec.parse("pdf"), FormatSpec.parse("pdf"))
    assert len(steps) == 1
    assert steps[0].capability == Capability.PDF_NORMALIZE


def test_plan_unsupported_identity_png() -> None:
    with pytest.raises(UnsupportedConversion):
        plan(FormatSpec.parse("png"), FormatSpec.parse("png"))


def test_execute_pdf_to_png(tmp_path: Path) -> None:
    src = TESTDATA / "regularity.pdf"
    dst = tmp_path / "out.png"
    steps = plan(FormatSpec.parse("pdf"), FormatSpec.parse("png"))
    result = execute(steps, src, dst)
    assert result == dst
    assert dst.exists() and dst.stat().st_size > 0
    # Verify it's a valid PNG
    import struct
    header = dst.read_bytes()[:8]
    assert header == b"\x89PNG\r\n\x1a\n", "output is not a PNG"


def test_execute_svg_to_pdf(tmp_path: Path) -> None:
    src = TESTDATA / "hello_glyphs.svg"
    dst = tmp_path / "out.pdf"
    steps = plan(FormatSpec.parse("svg"), FormatSpec.parse("pdf"))
    result = execute(steps, src, dst)
    assert result == dst
    assert dst.exists()
    assert dst.read_bytes()[:4] == b"%PDF", "output is not a PDF"


def test_execute_pdf_normalize(tmp_path: Path) -> None:
    src = TESTDATA / "papercut.pdf"
    dst = tmp_path / "norm.pdf"
    steps = plan(FormatSpec.parse("pdf"), FormatSpec.parse("pdf"))
    result = execute(steps, src, dst)
    assert result == dst
    assert dst.exists()
    assert dst.read_bytes()[:4] == b"%PDF", "normalized output is not a PDF"


def test_execute_backend_failure_wrapped(tmp_path: Path) -> None:
    # Pass a corrupt/nonexistent src — backend should raise BackendFailure
    src = tmp_path / "corrupt.pdf"
    src.write_bytes(b"not a pdf at all")
    dst = tmp_path / "out.png"
    steps = plan(FormatSpec.parse("pdf"), FormatSpec.parse("png"))
    with pytest.raises(BackendFailure) as exc_info:
        execute(steps, src, dst)
    assert exc_info.value.backend  # backend name is set
