from __future__ import annotations
# this_file: tests/test_dispatch.py
"""Tests for dispatch.py — capability table and resolve()."""

import pytest

from vexy_pdfsvgpy.dispatch import Capability, capability_table, resolve
from vexy_pdfsvgpy.errors import UnsupportedConversion
from vexy_pdfsvgpy.types import Hints


def test_capability_table_not_empty() -> None:
    table = capability_table()
    required = [
        Capability.PDF_TO_PNG,
        Capability.PDF_TO_SVG,
        Capability.SVG_TO_PDF,
        Capability.SVG_TO_PNG,
        Capability.PDF_NORMALIZE,
    ]
    for cap in required:
        assert table[cap], f"no backends registered for {cap}"


def test_resolve_pdf_to_svg_default() -> None:
    bf = resolve(Capability.PDF_TO_SVG)
    assert bf.name == "pymupdf", f"expected pymupdf, got {bf.name}"


def test_resolve_svg_to_png_resvg_default() -> None:
    bf = resolve(Capability.SVG_TO_PNG)
    assert bf.name == "resvg", f"expected resvg (inserted at front), got {bf.name}"


def test_resolve_with_hint_mu_on_svg_to_png() -> None:
    bf = resolve(Capability.SVG_TO_PNG, Hints.parse("mu"))
    assert bf.name == "pymupdf", f"expected pymupdf with hint mu, got {bf.name}"


def test_resolve_hint_no_match_falls_back_to_default() -> None:
    # Hint.RE is not in PDF_SPLIT candidates; should fall back to first entry
    bf = resolve(Capability.PDF_SPLIT, Hints.parse("re"))
    # pikepdf or pypdf — just confirm we got something without error
    assert bf.name in {"pikepdf", "pypdf", "apple"}


def test_hint_priority_ap_first() -> None:
    # ap,mu: if apple backend present it wins for PDF_NORMALIZE; else pymupdf
    bf = resolve(Capability.PDF_NORMALIZE, Hints.parse("ap,mu"))
    candidates = {b.name for b in capability_table()[Capability.PDF_NORMALIZE]}
    assert bf.name in candidates
    # If apple is available it should be picked first due to ap hint
    if "apple" in candidates:
        assert bf.name == "apple"
    else:
        assert bf.name == "pymupdf"


def test_resolve_unsupported_raises() -> None:
    import vexy_pdfsvgpy.dispatch as d
    # Temporarily clear a capability
    original = d._TABLE
    d._TABLE = {c: () if c == Capability.SVG_NORMALIZE else v
                for c, v in (d._TABLE or d._load_table()).items()}
    try:
        with pytest.raises(UnsupportedConversion, match="svg_normalize"):
            resolve(Capability.SVG_NORMALIZE)
    finally:
        d._TABLE = original
