from __future__ import annotations
# this_file: tests/backends/test_pdfium_backend.py
"""Tests for the pypdfium2 backend."""

from pathlib import Path

import pytest

from vexy_pdfsvgpy.backends import pdfium_backend as b

TESTDATA = Path(__file__).parent.parent.parent / "testdata"
POSTER_PDF = TESTDATA / "fontlab_posters.pdf"
PAPERCUT_PDF = TESTDATA / "papercut.pdf"
REGULARITY_PDF = TESTDATA / "regularity.pdf"


def test_pdf_page_count() -> None:
    count = b.pdf_page_count(POSTER_PDF)
    assert count >= 1, f"Expected at least 1 page, got {count}"


def test_pdf_to_png(tmp_path: Path) -> None:
    from PIL import Image

    out = tmp_path / "page0.png"
    result = b.pdf_to_png(REGULARITY_PDF, out, page=0, dpi=150)
    assert result == out
    assert out.exists(), "Output PNG was not created"
    img = Image.open(out)
    w, h = img.size
    assert w > 0 and h > 0, f"Image has zero dimension: {img.size}"


def test_pdf_to_png_dpi_scaling(tmp_path: Path) -> None:
    from PIL import Image

    out_low = tmp_path / "low.png"
    out_high = tmp_path / "high.png"
    b.pdf_to_png(REGULARITY_PDF, out_low, page=0, dpi=72)
    b.pdf_to_png(REGULARITY_PDF, out_high, page=0, dpi=300)
    w_low = Image.open(out_low).size[0]
    w_high = Image.open(out_high).size[0]
    expected_ratio = 300 / 72
    actual_ratio = w_high / w_low
    assert abs(actual_ratio - expected_ratio) / expected_ratio < 0.05, (
        f"DPI scaling off: expected ratio ~{expected_ratio:.3f}, got {actual_ratio:.3f} "
        f"(low={w_low}px, high={w_high}px)"
    )


def test_pdf_to_png_specific_page(tmp_path: Path) -> None:
    page_count = b.pdf_page_count(PAPERCUT_PDF)
    if page_count < 2:
        pytest.skip(f"papercut.pdf has only {page_count} page(s), need ≥2")
    from PIL import Image

    out = tmp_path / "page1.png"
    b.pdf_to_png(PAPERCUT_PDF, out, page=1, dpi=150)
    assert out.exists()
    img = Image.open(out)
    assert img.size[0] > 0 and img.size[1] > 0


def test_error_wrapping() -> None:
    with pytest.raises(RuntimeError, match=r"\[pdfium\]"):
        b.pdf_page_count(Path("/nonexistent/path/file.pdf"))
