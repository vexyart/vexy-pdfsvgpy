from __future__ import annotations
# this_file: tests/operations/test_color.py
"""Tests for operations/color.py."""

from pathlib import Path

import pytest
from PIL import Image

from vexy_pdfsvgpy.operations.color import ColorOptions, apply_color_bitmap, parse_color


def _make_png(tmp_path: Path, color: tuple[int, int, int, int], size: tuple[int, int] = (32, 32)) -> Path:
    p = tmp_path / f"fixture_{color[0]}_{color[1]}_{color[2]}.png"
    img = Image.new("RGBA", size, color)
    img.save(p, "PNG")
    return p


def test_parse_color_hex6() -> None:
    assert parse_color("#ff0000") == (255, 0, 0, 255)
    assert parse_color("#00ff00") == (0, 255, 0, 255)


def test_parse_color_hex8() -> None:
    assert parse_color("#ff000080") == (255, 0, 0, 128)


def test_parse_color_named() -> None:
    assert parse_color("white") == (255, 255, 255, 255)
    assert parse_color("black") == (0, 0, 0, 255)


def test_parse_color_dominant(tmp_path: Path) -> None:
    # 90% of the image is red (255,0,0,255)
    img = Image.new("RGBA", (100, 100), (255, 0, 0, 255))
    # small blue patch in corner
    for x in range(5):
        for y in range(5):
            img.putpixel((x, y), (0, 0, 255, 255))
    fixture = tmp_path / "dominant.png"
    img.save(fixture, "PNG")
    r, g, b, a = parse_color("dominant", ref_image=fixture)
    assert r > 200, f"expected dominant red, got ({r},{g},{b},{a})"


def test_apply_gray(tmp_path: Path) -> None:
    src = _make_png(tmp_path, (200, 50, 50, 255))
    dst = tmp_path / "gray.png"
    apply_color_bitmap(src, dst, ColorOptions(gray=True))
    with Image.open(dst).convert("RGBA") as out:
        pixels = list(out.getdata())  # type: ignore[arg-type]
    for r, g, b, _a in pixels:
        assert r == g == b, f"not gray: ({r},{g},{b})"


def test_apply_invert(tmp_path: Path) -> None:
    src = _make_png(tmp_path, (100, 150, 200, 255))
    dst = tmp_path / "inverted.png"
    apply_color_bitmap(src, dst, ColorOptions(invert=True))
    with Image.open(dst).convert("RGBA") as out:
        r2, g2, b2, _a = out.getpixel((0, 0))  # type: ignore[misc]
    assert r2 + 100 == 255
    assert g2 + 150 == 255
    assert b2 + 200 == 255


def test_apply_vivid(tmp_path: Path) -> None:
    src = _make_png(tmp_path, (200, 100, 50, 255))
    dst = tmp_path / "vivid.png"
    apply_color_bitmap(src, dst, ColorOptions(vivid=0.5))
    assert dst.exists()


def test_apply_bright_contrast(tmp_path: Path) -> None:
    src = _make_png(tmp_path, (100, 100, 100, 255))
    dst_b = tmp_path / "bright.png"
    dst_c = tmp_path / "contrast.png"
    apply_color_bitmap(src, dst_b, ColorOptions(bright=20.0))
    apply_color_bitmap(src, dst_c, ColorOptions(contrast=20.0))
    assert dst_b.exists()
    assert dst_c.exists()


def test_apply_backdrop(tmp_path: Path) -> None:
    # fully transparent PNG — compositing onto red should yield red pixels
    src = _make_png(tmp_path, (0, 0, 0, 0))
    dst = tmp_path / "backdrop.png"
    apply_color_bitmap(src, dst, ColorOptions(backdrop="#ff0000"))
    with Image.open(dst).convert("RGBA") as out:
        r, g, b, _a = out.getpixel((0, 0))  # type: ignore[misc]
    assert r == 255
    assert g == 0
    assert b == 0


def test_error_wrapping(tmp_path: Path) -> None:
    src = tmp_path / "nonexistent.png"
    dst = tmp_path / "out.png"
    with pytest.raises(RuntimeError, match=r"\[color\]"):
        apply_color_bitmap(src, dst, ColorOptions())
