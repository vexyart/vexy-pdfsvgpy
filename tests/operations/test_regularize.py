from __future__ import annotations
# this_file: tests/operations/test_regularize.py
"""Tests for operations/regularize.py."""

import platform
from pathlib import Path

import pytest

from vexy_pdfsvgpy.operations.regularize import regularize_pdf, regularize_svg

TESTDATA = Path(__file__).parent.parent.parent / "testdata"


def test_regularize_pdf_pymupdf(tmp_path: Path) -> None:
    src = TESTDATA / "papercut.pdf"
    dst = tmp_path / "norm.pdf"
    result = regularize_pdf(src, dst)
    assert result == dst
    assert dst.exists()
    content = dst.read_bytes()
    assert content[:4] == b"%PDF"
    # page count preserved
    import pymupdf
    src_doc = pymupdf.open(str(src))
    dst_doc = pymupdf.open(str(dst))
    assert len(dst_doc) == len(src_doc)
    src_doc.close()
    dst_doc.close()


def test_regularize_svg_pymupdf(tmp_path: Path) -> None:
    src = TESTDATA / "hello_glyphs.svg"
    dst = tmp_path / "norm.svg"
    result = regularize_svg(src, dst)
    assert result == dst
    assert dst.exists()
    from lxml import etree
    tree = etree.parse(str(dst))
    root = tree.getroot()
    assert "svg" in root.tag.lower()


def test_regularize_svg_resvg_wrap(tmp_path: Path) -> None:
    src = TESTDATA / "hello_glyphs.svg"
    dst = tmp_path / "norm_resvg.svg"
    result = regularize_svg(src, dst, backend="resvg")
    assert result == dst
    assert dst.exists()
    content = dst.read_text(encoding="utf-8")
    assert "data:image/png;base64," in content


@pytest.mark.skipif(
    platform.system() != "Darwin",
    reason="apple backend only available on macOS",
)
def test_regularize_pdf_apple_on_darwin(tmp_path: Path) -> None:
    src = TESTDATA / "papercut.pdf"
    dst = tmp_path / "norm_apple.pdf"
    result = regularize_pdf(src, dst, backend="apple")
    assert result == dst
    assert dst.exists()
    assert dst.read_bytes()[:4] == b"%PDF"


def test_regularize_error_wrapping(tmp_path: Path) -> None:
    src = tmp_path / "nonexistent.pdf"
    dst = tmp_path / "out.pdf"
    with pytest.raises(RuntimeError, match=r"\[regularize\]"):
        regularize_pdf(src, dst)
