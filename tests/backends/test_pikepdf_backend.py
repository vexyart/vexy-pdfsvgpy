from __future__ import annotations
# this_file: tests/backends/test_pikepdf_backend.py
"""Tests for pikepdf_backend — real calls, no mocks."""

from pathlib import Path

import pikepdf
import pytest

from vexy_pdfsvgpy.backends import pikepdf_backend as b

TESTDATA = Path(__file__).parent.parent.parent / "testdata"
REGULARITY = TESTDATA / "regularity.pdf"
PAPERCUT = TESTDATA / "papercut.pdf"


def _page_count(path: Path) -> int:
    pdf = pikepdf.open(str(path))
    try:
        return len(pdf.pages)
    finally:
        pdf.close()


def test_pdf_page_count() -> None:
    count = b.pdf_page_count(REGULARITY)
    assert count >= 1


def test_split_regularity(tmp_path: Path) -> None:
    outs = b.split(REGULARITY, tmp_path)
    assert len(outs) == b.pdf_page_count(REGULARITY)
    for p in outs:
        assert p.exists()
        assert _page_count(p) == 1


def test_split_filenames(tmp_path: Path) -> None:
    outs = b.split(REGULARITY, tmp_path, stem="mytest")
    # All names start with the given stem
    for p in outs:
        assert p.name.startswith("mytest-pikepdf-page-")
    # Padding is at least 2 digits
    first_name = outs[0].name
    # extract the number part: e.g. "mytest-pikepdf-page-01.pdf"
    num_part = first_name.rsplit("-", 1)[-1].replace(".pdf", "")
    assert len(num_part) >= 2


def test_merge_round_trip(tmp_path: Path) -> None:
    original_count = b.pdf_page_count(REGULARITY)
    pages = b.split(REGULARITY, tmp_path / "split")
    merged = b.merge(pages, tmp_path / "merged.pdf")
    assert merged.exists()
    assert _page_count(merged) == original_count


def test_overlay_two_pages(tmp_path: Path) -> None:
    # Split papercut to get individual pages; use first two (or first twice)
    pages = b.split(PAPERCUT, tmp_path / "split")
    base = pages[0]
    overlay = pages[1] if len(pages) >= 2 else pages[0]

    base_size = base.stat().st_size
    dst = tmp_path / "overlaid.pdf"
    result = b.overlay_pages(base, [overlay], dst)

    assert result.exists()
    assert _page_count(result) == 1
    assert result.stat().st_size > base_size


def test_error_wrapping() -> None:
    with pytest.raises(RuntimeError, match=r"\[pikepdf\]"):
        b.split(Path("/nonexistent/path/file.pdf"), Path("/tmp"))


def test_no_handle_leak_on_merge_failure(tmp_path: Path) -> None:
    # Split regularity to get one valid file
    pages = b.split(REGULARITY, tmp_path / "split")
    valid = pages[0]
    invalid = Path("/nonexistent/missing.pdf")

    with pytest.raises(RuntimeError, match=r"\[pikepdf\]"):
        b.merge([valid, invalid], tmp_path / "should_fail.pdf")

    # After failure, the valid file must still be openable (no lingering handles)
    pdf = pikepdf.open(str(valid))
    try:
        assert len(pdf.pages) == 1
    finally:
        pdf.close()
