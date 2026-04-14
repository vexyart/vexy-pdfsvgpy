from __future__ import annotations
# this_file: tests/backends/test_vtracer_backend.py
"""Tests for vtracer_backend — PNG/JPG → SVG vectorization."""

from pathlib import Path

import pytest
from PIL import Image
from lxml import etree

from vexy_pdfsvgpy.backends import vtracer_backend as b

try:
    from vexy_pdfsvgpy.backends import resvg_backend
    _RESVG_AVAILABLE = True
except (ImportError, ModuleNotFoundError):
    _RESVG_AVAILABLE = False


def _make_red_png(path: Path, size: int = 32) -> Path:
    Image.new("RGB", (size, size), "red").save(path)
    return path


def test_trace_synthetic_png(tmp_path: Path) -> None:
    src = _make_red_png(tmp_path / "input.png")
    dst = tmp_path / "output.svg"
    result = b.trace(src, dst)
    assert result == dst
    assert dst.exists()
    content = dst.read_text()
    assert content.startswith("<?xml") or content.startswith("<svg")


def test_trace_real_fixture(tmp_path: Path) -> None:
    tiger_svg = Path(__file__).parent.parent.parent / "testdata" / "tiger.svg"
    if not tiger_svg.exists():
        pytest.skip("testdata/tiger.svg not found")
    if not _RESVG_AVAILABLE:
        pytest.skip("resvg_backend not available yet")

    png_path = tmp_path / "tiger.png"
    resvg_backend.svg_to_png(tiger_svg, png_path, width=256)
    assert png_path.exists(), "resvg_backend failed to produce PNG"

    dst = tmp_path / "tiger_traced.svg"
    b.trace(png_path, dst)
    assert dst.exists()

    root = etree.fromstring(dst.read_bytes())
    ns = {"svg": "http://www.w3.org/2000/svg"}
    paths = root.findall(".//svg:path", ns) or root.findall(".//{*}path")
    assert len(paths) >= 1, "Expected at least one <path> in traced SVG"


def test_trace_binary_mode(tmp_path: Path) -> None:
    src = _make_red_png(tmp_path / "input_bin.png")
    dst = tmp_path / "output_bin.svg"
    result = b.trace(src, dst, colormode="binary")
    assert result == dst
    assert dst.exists()
    content = dst.read_text()
    assert content.startswith("<?xml") or content.startswith("<svg")


def test_error_wrapping(tmp_path: Path) -> None:
    src = tmp_path / "nonexistent.png"
    dst = tmp_path / "out.svg"
    with pytest.raises(RuntimeError, match=r"\[vtracer\]"):
        b.trace(src, dst)


def test_output_is_lxml_parseable(tmp_path: Path) -> None:
    src = _make_red_png(tmp_path / "input2.png")
    dst = tmp_path / "output2.svg"
    b.trace(src, dst)
    # Should not raise
    root = etree.fromstring(dst.read_bytes())
    assert root is not None
