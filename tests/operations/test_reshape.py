from __future__ import annotations
# this_file: tests/operations/test_reshape.py
"""Tests for reshape operations (Phase 5)."""

from pathlib import Path

import pytest

from vexy_pdfsvgpy.operations import reshape

TESTDATA = Path(__file__).parent.parent.parent / "testdata"
FONTLAB = TESTDATA / "fontlab_posters.pdf"
REGULARITY = TESTDATA / "regularity.pdf"
PAPERCUT = TESTDATA / "papercut.pdf"
HELLO_SVG = TESTDATA / "hello_glyphs.svg"
INITIAL_SVG = TESTDATA / "initial.svg"

NS_INKSCAPE = "http://www.inkscape.org/namespaces/inkscape"
NS_SVG = "http://www.w3.org/2000/svg"
_LAYER_ATTR = f"{{{NS_INKSCAPE}}}groupmode"


def test_pages2docs_pdf_and_back(tmp_path: Path) -> None:
    """Split fontlab_posters.pdf into per-page PDFs, then merge back."""
    import pikepdf

    split_dir = tmp_path / "split"
    pages = reshape.pages2docs_pdf(FONTLAB, split_dir)
    assert len(pages) >= 2, "expected multiple pages"
    for p in pages:
        assert p.exists()
        pdf = pikepdf.Pdf.open(str(p))
        assert len(pdf.pages) == 1
        pdf.close()

    # original page count
    orig = pikepdf.Pdf.open(str(FONTLAB))
    orig_count = len(orig.pages)
    orig.close()

    merged = tmp_path / "merged.pdf"
    reshape.docs2pages_pdf(pages, merged)
    assert merged.exists()
    merged_pdf = pikepdf.Pdf.open(str(merged))
    assert len(merged_pdf.pages) == orig_count
    merged_pdf.close()


def test_docs2layers_pdf_two_sources(tmp_path: Path) -> None:
    """Stack two PDFs as OCG layers; verify OCG names."""
    import pymupdf

    # get one page from each source
    reg_pages = reshape.pages2docs_pdf(REGULARITY, tmp_path / "reg", stem="reg")
    pk_pages = reshape.pages2docs_pdf(PAPERCUT, tmp_path / "pk", stem="pk")
    srcs = [reg_pages[0], pk_pages[0]]

    layered = tmp_path / "layered.pdf"
    reshape.docs2layers_pdf(srcs, layered, labels=["Regularity", "Papercut"])
    assert layered.exists()

    doc = pymupdf.open(str(layered))
    ocgs = doc.get_ocgs()
    doc.close()

    assert len(ocgs) == 2
    names = {v["name"] for v in ocgs.values()}
    assert names == {"Regularity", "Papercut"}


def test_docs2layers_svg_two_sources(tmp_path: Path) -> None:
    """Stack two SVGs as Inkscape layers; verify structure."""
    from lxml import etree

    out = tmp_path / "layered.svg"
    reshape.docs2layers_svg([HELLO_SVG, INITIAL_SVG], out)
    assert out.exists()

    root = etree.parse(str(out)).getroot()
    assert root.tag == f"{{{NS_SVG}}}svg"
    assert NS_INKSCAPE in root.nsmap.values()

    layer_groups = [el for el in root if el.get(_LAYER_ATTR) == "layer"]
    assert len(layer_groups) == 2
    assert layer_groups[0].get(f"{{{NS_INKSCAPE}}}label") == "Layer 1"
    assert layer_groups[1].get(f"{{{NS_INKSCAPE}}}label") == "Layer 2"

    # width/height/viewBox from first source (fallback to defaults when absent)
    first_root = etree.parse(str(HELLO_SVG)).getroot()
    expected_width = first_root.get("width") or "800"
    expected_height = first_root.get("height") or "600"
    assert root.get("width") == expected_width
    assert root.get("height") == expected_height


def test_layers2docs_svg_round_trip(tmp_path: Path) -> None:
    """Round-trip: compose layers then split back; check element counts."""
    from lxml import etree

    layered = tmp_path / "layered.svg"
    reshape.docs2layers_svg([HELLO_SVG, INITIAL_SVG], layered)

    split_dir = tmp_path / "split_svg"
    parts = reshape.layers2docs_svg(layered, split_dir)
    assert len(parts) == 2
    for p in parts:
        assert p.exists()
        r = etree.parse(str(p)).getroot()
        assert r.tag == f"{{{NS_SVG}}}svg"
        assert len(r) > 0  # has children

    # element count in first part should match hello_glyphs children count
    hello_root = etree.parse(str(HELLO_SVG)).getroot()
    part0_root = etree.parse(str(parts[0])).getroot()
    assert len(part0_root) == len(hello_root)


def test_docs2layers_pdf_custom_labels(tmp_path: Path) -> None:
    """Stack with explicit labels and verify OCG names match."""
    import pymupdf

    pages = reshape.pages2docs_pdf(FONTLAB, tmp_path / "p")
    srcs = pages[:3]
    labels = ["Foo", "Bar", "Baz"]
    out = tmp_path / "custom.pdf"
    reshape.docs2layers_pdf(srcs, out, labels=labels)

    doc = pymupdf.open(str(out))
    ocgs = doc.get_ocgs()
    doc.close()
    names = {v["name"] for v in ocgs.values()}
    assert names == set(labels)


def test_docs2layers_pdf_default_labels(tmp_path: Path) -> None:
    """Stack without labels; verify defaults are 'Layer 1', 'Layer 2'."""
    import pymupdf

    pages = reshape.pages2docs_pdf(REGULARITY, tmp_path / "r")
    srcs = pages[:2]
    out = tmp_path / "default_labels.pdf"
    reshape.docs2layers_pdf(srcs, out)

    doc = pymupdf.open(str(out))
    ocgs = doc.get_ocgs()
    doc.close()
    names = {v["name"] for v in ocgs.values()}
    assert names == {"Layer 1", "Layer 2"}


def test_error_wrapping_reshape(tmp_path: Path) -> None:
    """Nonexistent source raises RuntimeError with [reshape] prefix."""
    bad = tmp_path / "nonexistent.pdf"
    with pytest.raises(RuntimeError, match=r"\[reshape\]"):
        reshape.docs2layers_pdf([bad], tmp_path / "out.pdf")
