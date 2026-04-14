from __future__ import annotations
# this_file: tests/backends/test_apple_backend.py
"""Tests for apple_backend — PDFKit + CoreGraphics (macOS only)."""

import sys
from pathlib import Path

import pytest

from vexy_pdfsvgpy.backends import apple_backend as b

TESTDATA = Path(__file__).parent.parent.parent / "testdata"
REGULARITY = TESTDATA / "regularity.pdf"
PAPERCUT = TESTDATA / "papercut.pdf"
FONTLAB = TESTDATA / "fontlab_posters.pdf"

darwin_only = pytest.mark.skipif(sys.platform != "darwin", reason="apple_backend is macOS-only")


@darwin_only
def test_pdf_page_count():
    count = b.pdf_page_count(REGULARITY)
    assert count >= 1


@darwin_only
def test_pdf_normalize(tmp_path):
    dst = tmp_path / "normalized.pdf"
    original_count = b.pdf_page_count(PAPERCUT)
    result = b.pdf_normalize(PAPERCUT, dst)
    assert result == dst
    assert dst.exists()
    assert dst.read_bytes()[:4] == b"%PDF"
    assert b.pdf_page_count(dst) == original_count


@darwin_only
def test_split(tmp_path):
    out_dir = tmp_path / "split_out"
    outputs = b.split(REGULARITY, out_dir)
    assert isinstance(outputs, list)
    assert len(outputs) >= 1
    for p in outputs:
        assert p.exists(), f"Expected {p} to exist"
        assert b.pdf_page_count(p) == 1


@darwin_only
def test_merge(tmp_path):
    original_count = b.pdf_page_count(REGULARITY)
    out_dir = tmp_path / "split_reg"
    parts = b.split(REGULARITY, out_dir)
    merged = b.merge(parts, tmp_path / "merged.pdf")
    assert merged.exists()
    assert b.pdf_page_count(merged) == original_count


@darwin_only
def test_pdf_to_png(tmp_path):
    dst = tmp_path / "page0.png"
    result = b.pdf_to_png(FONTLAB, dst, page=0, width=1024)
    assert result == dst
    assert dst.exists()
    from PIL import Image
    img = Image.open(dst)
    assert abs(img.width - 1024) <= 2, f"Expected width ~1024, got {img.width}"


def test_error_on_non_darwin(monkeypatch, tmp_path):
    monkeypatch.setattr(b, "IS_DARWIN", False)
    with pytest.raises(RuntimeError, match=r"\[apple\]"):
        b.pdf_normalize(PAPERCUT, tmp_path / "out.pdf")


def test_unsupported_platform_message(monkeypatch, tmp_path):
    monkeypatch.setattr(b, "IS_DARWIN", False)
    monkeypatch.setattr(sys, "platform", "linux")
    with pytest.raises(RuntimeError, match=r"\[apple\] pdf_normalize unsupported on linux"):
        b.pdf_normalize(PAPERCUT, tmp_path / "out.pdf")
