from __future__ import annotations
# this_file: tests/test_convert.py
"""End-to-end tests for the public convert() API."""

from pathlib import Path

import pytest

from vexy_pdfsvgpy import convert
from vexy_pdfsvgpy.errors import InvalidInput, UnsupportedConversion

TESTDATA = Path(__file__).parent.parent / "testdata"


def test_convert_pdf_to_png_via_ext_inference(tmp_path: Path) -> None:
    out = convert(
        input=str(TESTDATA / "regularity.pdf"),
        output=str(tmp_path / "out.png"),
    )
    assert out.exists()
    assert out.read_bytes()[:8] == b"\x89PNG\r\n\x1a\n"


def test_convert_svg_to_pdf_via_ext_inference(tmp_path: Path) -> None:
    out = convert(
        input=str(TESTDATA / "hello_glyphs.svg"),
        output=str(tmp_path / "out.pdf"),
    )
    assert out.exists()
    assert out.read_bytes()[:4] == b"%PDF"


def test_convert_svg_to_png(tmp_path: Path) -> None:
    out = convert(
        input=str(TESTDATA / "tiger.svg"),
        output=str(tmp_path / "tiger.png"),
    )
    assert out.exists()
    assert out.stat().st_size > 0
    # Check PNG dimensions are non-zero via struct
    import struct
    data = out.read_bytes()
    assert data[:8] == b"\x89PNG\r\n\x1a\n"
    # PNG IHDR chunk: bytes 16-20 = width, 20-24 = height
    width = struct.unpack(">I", data[16:20])[0]
    assert width > 0


def test_convert_with_hint_mu_on_svg_to_png(tmp_path: Path) -> None:
    # Force pymupdf for SVG→PNG with hint "mu"
    out_mu = tmp_path / "tiger_mu.png"
    convert(
        input=str(TESTDATA / "tiger.svg"),
        output=str(out_mu),
        hints="mu",
    )
    assert out_mu.exists() and out_mu.stat().st_size > 0

    import struct
    data = out_mu.read_bytes()
    width = struct.unpack(">I", data[16:20])[0]
    assert width > 0


def test_convert_missing_input_raises_invalid_input(tmp_path: Path) -> None:
    with pytest.raises(InvalidInput):
        convert(
            input=str(tmp_path / "nonexistent.pdf"),
            output=str(tmp_path / "out.png"),
        )


def test_convert_unsupported_conversion_raises(tmp_path: Path) -> None:
    # png → png is identity but not supported
    src = tmp_path / "dummy.png"
    src.write_bytes(b"\x89PNG\r\n\x1a\n" + b"\x00" * 20)
    with pytest.raises(UnsupportedConversion):
        convert(input=str(src), output=str(tmp_path / "out.png"))


def test_convert_returns_output_path(tmp_path: Path) -> None:
    expected = tmp_path / "out.pdf"
    result = convert(
        input=str(TESTDATA / "hello_glyphs.svg"),
        output=str(expected),
    )
    assert result == expected
