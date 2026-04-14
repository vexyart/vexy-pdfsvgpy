from __future__ import annotations

# this_file: tests/backends/test_pymupdf_backend.py

from pathlib import Path

import pytest
from PIL import Image

from vexy_pdfsvgpy.backends import pymupdf_backend as b

TESTDATA = Path(__file__).parent.parent.parent / "testdata"


def test_pdf_page_count() -> None:
    result = b.pdf_page_count(TESTDATA / "regularity.pdf")
    assert isinstance(result, int)
    assert result >= 1


def test_pdf_page_size() -> None:
    w, h = b.pdf_page_size(TESTDATA / "fontlab_posters.pdf", page=0)
    assert isinstance(w, float)
    assert isinstance(h, float)
    assert w > 0
    assert h > 0


def test_pdf_to_png(tmp_path: Path) -> None:
    dst = tmp_path / "out.png"
    result = b.pdf_to_png(TESTDATA / "regularity.pdf", dst, page=0, dpi=150)
    assert result == dst
    assert dst.exists()
    assert dst.stat().st_size > 0
    img = Image.open(dst)
    assert img.size[0] > 0


def test_pdf_to_svg(tmp_path: Path) -> None:
    dst = tmp_path / "out.svg"
    result = b.pdf_to_svg(TESTDATA / "fontlab_posters.pdf", dst, page=0)
    assert result == dst
    assert dst.exists()
    content = dst.read_text(encoding="utf-8").lstrip()
    assert content.startswith("<?xml") or content.startswith("<svg")


def test_svg_to_pdf(tmp_path: Path) -> None:
    dst = tmp_path / "out.pdf"
    result = b.svg_to_pdf(TESTDATA / "hello_glyphs.svg", dst)
    assert result == dst
    assert dst.exists()
    header = dst.read_bytes()[:8]
    assert header.startswith(b"%PDF-")


def test_svg_to_png(tmp_path: Path) -> None:
    dst = tmp_path / "out.png"
    result = b.svg_to_png(TESTDATA / "tiger.svg", dst, dpi=150)
    assert result == dst
    assert dst.exists()
    assert dst.stat().st_size > 0
    img = Image.open(dst)
    assert img.size[0] > 0


def test_pdf_normalize(tmp_path: Path) -> None:
    src = TESTDATA / "papercut.pdf"
    dst = tmp_path / "normalized.pdf"
    result = b.pdf_normalize(src, dst)
    assert result == dst
    assert dst.exists()
    header = dst.read_bytes()[:8]
    assert header.startswith(b"%PDF-")
    assert b.pdf_page_count(dst) == b.pdf_page_count(src)


def test_svg_normalize(tmp_path: Path) -> None:
    dst = tmp_path / "normalized.svg"
    result = b.svg_normalize(TESTDATA / "initial.svg", dst)
    assert result == dst
    assert dst.exists()
    content = dst.read_text(encoding="utf-8")
    assert "<svg" in content
    from lxml import etree
    etree.fromstring(content.encode("utf-8"))


def test_error_wrapping(tmp_path: Path) -> None:
    with pytest.raises(RuntimeError, match=r"\[pymupdf\]"):
        b.pdf_to_png(Path("/nonexistent/file.pdf"), tmp_path / "out.png")
