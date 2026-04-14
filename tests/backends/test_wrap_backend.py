from __future__ import annotations
# this_file: tests/backends/test_wrap_backend.py
"""Tests for wrap_backend — bitmap-to-SVG/PDF wrapping."""

import pytest
from pathlib import Path
from PIL import Image


def _make_png(path: Path, size: tuple[int, int] = (32, 32), color: str = "red") -> Path:
    img = Image.new("RGB", size, color)
    img.save(path, format="PNG")
    return path


def _make_jpg(path: Path, size: tuple[int, int] = (32, 32), color: str = "green") -> Path:
    img = Image.new("RGB", size, color)
    img.save(path, format="JPEG")
    return path


def test_png_to_svg(tmp_path: Path) -> None:
    from vexy_pdfsvgpy.backends import wrap_backend as b

    src = _make_png(tmp_path / "in.png", (32, 32))
    dst = tmp_path / "out.svg"
    result = b.png_to_svg(src, dst)

    assert result == dst
    assert dst.exists()
    text = dst.read_text()
    assert text.startswith("<?xml") or text.startswith("<svg")
    assert 'xlink:href="data:image/png;base64,' in text

    from lxml import etree

    root = etree.fromstring(dst.read_bytes())
    assert root.get("width") == "32"
    assert root.get("height") == "32"


def test_jpg_to_svg(tmp_path: Path) -> None:
    from vexy_pdfsvgpy.backends import wrap_backend as b

    src = _make_jpg(tmp_path / "in.jpg", (32, 32))
    dst = tmp_path / "out.svg"
    result = b.jpg_to_svg(src, dst)

    assert result == dst
    text = dst.read_text()
    assert 'xlink:href="data:image/jpeg;base64,' in text

    from lxml import etree

    root = etree.fromstring(dst.read_bytes())
    assert root.get("width") == "32"
    assert root.get("height") == "32"


def test_svg_round_trips_through_resvg(tmp_path: Path) -> None:
    pytest.importorskip("resvg_py", reason="resvg_py not available")
    from vexy_pdfsvgpy.backends import wrap_backend as b

    try:
        from vexy_pdfsvgpy.backends import resvg_backend
    except Exception:
        pytest.skip("resvg_backend not importable")

    src = _make_png(tmp_path / "in.png", (24, 24))
    svg = tmp_path / "wrapped.svg"
    b.png_to_svg(src, svg)

    out_png = tmp_path / "round.png"
    resvg_backend.svg_to_png(svg, out_png)
    assert out_png.exists()

    with Image.open(out_png) as img:
        w, h = img.size
    assert w >= 24
    assert h >= 24


def test_png_to_pdf(tmp_path: Path) -> None:
    from vexy_pdfsvgpy.backends import wrap_backend as b

    src = _make_png(tmp_path / "in.png", (64, 64))
    dst = tmp_path / "out.pdf"
    result = b.png_to_pdf(src, dst)

    assert result == dst
    assert dst.exists()
    raw = dst.read_bytes()
    assert raw[:5] == b"%PDF-"

    import pymupdf

    doc = pymupdf.open(str(dst))
    try:
        assert doc.page_count == 1
    finally:
        doc.close()


def test_bitmap_to_svg_auto_mime(tmp_path: Path) -> None:
    from vexy_pdfsvgpy.backends import wrap_backend as b

    png_src = _make_png(tmp_path / "img.png")
    png_dst = tmp_path / "png_out.svg"
    b.bitmap_to_svg(png_src, png_dst)
    assert 'data:image/png;base64,' in png_dst.read_text()

    jpg_src = _make_jpg(tmp_path / "img.jpg")
    jpg_dst = tmp_path / "jpg_out.svg"
    b.bitmap_to_svg(jpg_src, jpg_dst)
    assert 'data:image/jpeg;base64,' in jpg_dst.read_text()


def test_bitmap_to_svg_unknown_ext(tmp_path: Path) -> None:
    from vexy_pdfsvgpy.backends import wrap_backend as b

    fake = tmp_path / "file.xyz"
    fake.write_bytes(b"\x00\x01\x02")
    with pytest.raises(RuntimeError, match=r"\[wrap\]"):
        b.bitmap_to_svg(fake, tmp_path / "out.svg")


def test_error_wrapping(tmp_path: Path) -> None:
    from vexy_pdfsvgpy.backends import wrap_backend as b

    nonexistent = tmp_path / "ghost.png"
    with pytest.raises(RuntimeError, match=r"\[wrap\]"):
        b.png_to_svg(nonexistent, tmp_path / "out.svg")
