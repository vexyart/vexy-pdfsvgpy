from __future__ import annotations
# this_file: tests/test_document.py
"""Tests for vexy_pdfsvgpy.document — Document and Page intermediate types."""

import struct
import zlib
from pathlib import Path

import pytest

from vexy_pdfsvgpy.document import Document, Page
from vexy_pdfsvgpy.errors import InvalidInput
from vexy_pdfsvgpy.types import FormatSpec

TESTDATA = Path(__file__).parent.parent / "testdata"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_tiny_png(path: Path, width: int = 3, height: int = 3) -> Path:
    """Write a minimal valid 3×3 red PNG to *path* without Pillow."""
    def _chunk(tag: bytes, data: bytes) -> bytes:
        c = struct.pack(">I", len(data)) + tag + data
        return c + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)

    # IHDR
    ihdr = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    # Raw image: filter byte 0 + RGB pixels
    raw = b"".join(b"\x00" + b"\xFF\x00\x00" * width for _ in range(height))
    idat = zlib.compress(raw)

    png = b"\x89PNG\r\n\x1a\n"
    png += _chunk(b"IHDR", ihdr)
    png += _chunk(b"IDAT", idat)
    png += _chunk(b"IEND", b"")
    path.write_bytes(png)
    return path


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_empty_document() -> None:
    d = Document.empty()
    assert len(d) == 0
    assert not d
    assert d.page_count == 0
    assert d.kind is None


def test_from_path_pdf() -> None:
    d = Document.from_path(TESTDATA / "regularity.pdf")
    assert d.source is not None
    assert d.source.name == "regularity.pdf"
    assert d.spec is not None
    assert d.spec.format == "pdf"
    assert len(d) == 1, "placeholder page expected"


def test_from_path_svg() -> None:
    d = Document.from_path(TESTDATA / "hello_glyphs.svg")
    assert d.source is not None
    assert d.source.name == "hello_glyphs.svg"
    assert d.spec is not None
    assert d.spec.format == "svg"
    assert len(d) == 1


def test_from_path_png(tmp_path: Path) -> None:
    png = _make_tiny_png(tmp_path / "red.png")
    d = Document.from_path(png)
    assert d.spec is not None
    assert d.spec.format == "png"
    assert len(d) == 1


def test_from_path_missing() -> None:
    with pytest.raises(InvalidInput, match="does not exist"):
        Document.from_path("/nonexistent/path/file.pdf")


def test_from_path_unknown_ext(tmp_path: Path) -> None:
    f = tmp_path / "data.xyz"
    f.write_bytes(b"dummy")
    with pytest.raises(InvalidInput):
        Document.from_path(f)


def test_explicit_spec_overrides_extension(tmp_path: Path) -> None:
    # File has .svg extension but we pass an explicit pdf-m spec.
    f = tmp_path / "doc.svg"
    f.write_bytes(b"<svg/>")
    spec = FormatSpec.parse("pdf-mo")
    d = Document.from_path(f, spec=spec)
    assert d.spec == spec
    assert d.spec.format == "pdf"


def test_add_page() -> None:
    d = Document.empty()
    p = Page(content=b"", kind="png", width=100.0, height=100.0)
    d.add(p)
    assert len(d) == 1
    assert d.kind == "png"
    assert bool(d)


def test_dataclass_slots() -> None:
    d = Document.empty()
    with pytest.raises(AttributeError):
        d.unexpected_attribute = "boom"  # type: ignore[attr-defined]

    p = Page(content=b"", kind="pdf", width=0.0, height=0.0)
    with pytest.raises(AttributeError):
        p.unexpected_attribute = "boom"  # type: ignore[attr-defined]
