from __future__ import annotations
# this_file: tests/operations/test_sizecrop.py
"""Tests for operations/sizecrop.py."""

from pathlib import Path

import pytest

from vexy_pdfsvgpy.operations.sizecrop import (
    SizeCropOptions,
    apply_sizecrop_pdf,
    compute_scale,
    parse_dim,
    resolve_dim,
    resolve_margins,
)

TESTDATA = Path(__file__).parent.parent.parent / "testdata"


def test_parse_dim_wxh() -> None:
    assert parse_dim("800x600") == (800, 600)
    assert parse_dim("none") is None
    with pytest.raises(RuntimeError, match=r"\[sizecrop\]"):
        parse_dim("bad")


def test_resolve_dim_modes() -> None:
    sources = [(100, 200), (300, 400)]
    assert resolve_dim(sources, "first") == (100, 200)
    assert resolve_dim(sources, "last") == (300, 400)
    assert resolve_dim(sources, "largest") == (300, 400)  # 300*400 > 100*200
    assert resolve_dim(sources, "none") is None
    assert resolve_dim([], "first") is None


def test_compute_scale_fit() -> None:
    # source (100,50), target (200,200): fit → min(200/100, 200/50) = min(2.0, 4.0) = 2.0
    result = compute_scale((100, 50), (200, 200), "fit")
    assert result == pytest.approx(2.0)


def test_compute_scale_keep() -> None:
    assert compute_scale((100, 200), (999, 999), "keep") == pytest.approx(1.0)


def test_compute_scale_percent() -> None:
    assert compute_scale((100, 100), (200, 200), 50) == pytest.approx(0.5)


def test_compute_scale_width_height() -> None:
    assert compute_scale((100, 100), (200, 300), "width") == pytest.approx(2.0)
    assert compute_scale((100, 100), (200, 300), "height") == pytest.approx(3.0)


def test_resolve_margins_auto() -> None:
    assert resolve_margins(10.0, None, None, None) == (10.0, 0.0, 0.0, 0.0)
    assert resolve_margins(None, None, None, None) == (0.0, 0.0, 0.0, 0.0)


def test_apply_sizecrop_pdf_passthrough(tmp_path: Path) -> None:
    src = TESTDATA / "regularity.pdf"
    dst = tmp_path / "out.pdf"
    opts = SizeCropOptions(dim="none")
    result = apply_sizecrop_pdf(src, dst, opts)
    assert result == dst
    assert dst.exists()
    assert dst.read_bytes()[:4] == b"%PDF"
    import pymupdf
    src_doc = pymupdf.open(str(src))
    dst_doc = pymupdf.open(str(dst))
    assert len(dst_doc) == len(src_doc)
    src_doc.close()
    dst_doc.close()


def test_apply_sizecrop_pdf_largest(tmp_path: Path) -> None:
    src = TESTDATA / "regularity.pdf"
    dst = tmp_path / "largest.pdf"
    import pymupdf
    src_doc = pymupdf.open(str(src))
    sources = [(int(src_doc[i].rect.width), int(src_doc[i].rect.height)) for i in range(len(src_doc))]
    src_doc.close()
    largest = max(sources, key=lambda wh: wh[0] * wh[1])
    opts = SizeCropOptions(dim="largest", scale="fit")
    result = apply_sizecrop_pdf(src, dst, opts)
    assert result == dst
    assert dst.exists()
    out_doc = pymupdf.open(str(dst))
    out_w = int(out_doc[0].rect.width)
    out_h = int(out_doc[0].rect.height)
    out_doc.close()
    assert (out_w, out_h) == largest


def test_apply_sizecrop_pdf_explicit_dim(tmp_path: Path) -> None:
    src = TESTDATA / "papercut.pdf"
    dst = tmp_path / "sized.pdf"
    opts = SizeCropOptions(dim="800x600", scale="fit")
    result = apply_sizecrop_pdf(src, dst, opts)
    assert result == dst
    assert dst.exists()
    import pymupdf
    out_doc = pymupdf.open(str(dst))
    page_rect = out_doc[0].rect
    out_doc.close()
    assert int(page_rect.width) == 800
    assert int(page_rect.height) == 600
