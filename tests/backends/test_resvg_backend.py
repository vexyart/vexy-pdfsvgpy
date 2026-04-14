from __future__ import annotations
# this_file: tests/backends/test_resvg_backend.py
"""Tests for resvg_backend — real resvg_py calls, no mocks."""

from pathlib import Path

import pytest
from PIL import Image

from vexy_pdfsvgpy.backends import resvg_backend as b

TESTDATA = Path(__file__).parent.parent.parent / "testdata"
TIGER = TESTDATA / "tiger.svg"
HELLO = TESTDATA / "hello_glyphs.svg"
INITIAL = TESTDATA / "initial.svg"

PT_SVG = """\
<svg xmlns="http://www.w3.org/2000/svg" width="100pt" height="50pt" viewBox="0 0 100 50">
  <rect width="100" height="50" fill="red"/>
</svg>
"""

SIMPLE_SVG = (
    "<svg xmlns='http://www.w3.org/2000/svg' width='100' height='100'>"
    "<rect width='100' height='100' fill='blue'/></svg>"
)


def test_svg_to_png_tiger(tmp_path: Path) -> None:
    dst = tmp_path / "tiger.png"
    b.svg_to_png(TIGER, dst, width=512)
    assert dst.exists()
    img = Image.open(dst)
    assert img.width == 512


def test_svg_to_png_width_scales(tmp_path: Path) -> None:
    dst1024 = tmp_path / "tiger_1024.png"
    dst2048 = tmp_path / "tiger_2048.png"
    b.svg_to_png(TIGER, dst1024, width=1024)
    b.svg_to_png(TIGER, dst2048, width=2048)
    assert Image.open(dst1024).width == 1024
    assert Image.open(dst2048).width == 2048


def test_pt_fallback(tmp_path: Path) -> None:
    src = tmp_path / "pt_units.svg"
    src.write_text(PT_SVG, encoding="utf-8")
    dst = tmp_path / "pt_units.png"
    # Either resvg handles pt natively or triggers the fallback — both are fine.
    b.svg_to_png(src, dst, width=2048)
    assert dst.exists()
    img = Image.open(dst)
    assert img.width > 0


def test_svg_to_png_bytes_from_string(tmp_path: Path) -> None:
    png = b.svg_to_png_bytes(SIMPLE_SVG, width=256)
    assert isinstance(png, bytes)
    assert png[:4] == b"\x89PNG"
    img = Image.open(__import__("io").BytesIO(png))
    assert img.width == 256
    assert img.height == 256


def test_error_wrapping(tmp_path: Path) -> None:
    missing = tmp_path / "does_not_exist.svg"
    with pytest.raises(RuntimeError, match=r"\[resvg\]"):
        b.svg_to_png(missing, tmp_path / "out.png")


def test_real_fixture_hello_glyphs(tmp_path: Path) -> None:
    dst = tmp_path / "hello.png"
    b.svg_to_png(HELLO, dst, width=1024)
    assert dst.exists()
    assert Image.open(dst).width > 0


def test_real_fixture_initial(tmp_path: Path) -> None:
    dst = tmp_path / "initial.png"
    b.svg_to_png(INITIAL, dst, width=1024)
    assert dst.exists()
    assert Image.open(dst).width > 0
