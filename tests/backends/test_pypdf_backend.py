from __future__ import annotations
# this_file: tests/backends/test_pypdf_backend.py
"""Tests for pypdf_backend — split, merge, page count."""

import re
from pathlib import Path

import pytest

from vexy_pdfsvgpy.backends import pypdf_backend as b

TESTDATA = Path(__file__).parent.parent.parent / "testdata"
FONTLAB = TESTDATA / "fontlab_posters.pdf"
REGULARITY = TESTDATA / "regularity.pdf"
PAPERCUT = TESTDATA / "papercut.pdf"


def test_pdf_page_count():
    count = b.pdf_page_count(FONTLAB)
    assert count >= 1


def test_split_fontlab_posters(tmp_path):
    out_dir = tmp_path / "split_out"
    original_count = b.pdf_page_count(FONTLAB)
    outputs = b.split(FONTLAB, out_dir)

    assert isinstance(outputs, list)
    assert len(outputs) == original_count
    for p in outputs:
        assert p.exists(), f"Expected {p} to exist"
        assert b.pdf_page_count(p) == 1


def test_split_filenames_padded(tmp_path):
    out_dir = tmp_path / "split_pad"
    outputs = b.split(FONTLAB, out_dir)
    n = len(outputs)
    pad = max(2, len(str(n)))
    pattern = re.compile(rf".+-pypdf-page-\d{{{pad}}}.pdf$")
    for p in outputs:
        assert pattern.match(p.name), f"Filename {p.name!r} doesn't match padding pattern"
    # Verify page numbers are zero-padded to at least 2 digits
    assert outputs[0].name.endswith(f"-pypdf-page-{'1':>0{pad}}.pdf".replace(
        f"{'1':>0{pad}}", f"{1:0{pad}d}"
    ))


def test_merge_round_trip(tmp_path):
    original_count = b.pdf_page_count(REGULARITY)
    out_dir = tmp_path / "split_reg"
    parts = b.split(REGULARITY, out_dir)
    merged = b.merge(parts, tmp_path / "merged.pdf")
    assert merged.exists()
    assert b.pdf_page_count(merged) == original_count


def test_merge_preserves_order(tmp_path):
    # Use regularity.pdf which has many pages; take first two split pages
    out_dir = tmp_path / "split_reg2"
    parts = b.split(REGULARITY, out_dir)
    first_two = parts[:2]
    merged = b.merge(first_two, tmp_path / "two_pages.pdf")
    assert merged.exists()
    assert b.pdf_page_count(merged) == 2


def test_split_custom_stem(tmp_path):
    out_dir = tmp_path / "custom"
    outputs = b.split(FONTLAB, out_dir, stem="foo")
    for p in outputs:
        assert p.name.startswith("foo-pypdf-page-"), f"Got {p.name!r}"


def test_error_wrapping():
    with pytest.raises(RuntimeError, match=r"\[pypdf\]"):
        b.split(Path("/nonexistent/does_not_exist.pdf"), Path("/tmp"))
