# this_file: tests/test_types.py
"""Tests for FormatSpec, Hints, and error classes."""
from __future__ import annotations

from pathlib import Path

import pytest

from vexy_pdfsvgpy.errors import BackendFailure, InvalidInput
from vexy_pdfsvgpy.types import FormatSpec, Hint, Hints, Packaging, Content


# ---------------------------------------------------------------------------
# FormatSpec.parse — valid round-trips
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    ("input_str", "expected_str"),
    [
        ("pdf", "pdf"),
        ("pdf-d", "pdf"),
        ("pdf-do", "pdf"),
        ("pdf-m", "pdf-mo"),
        ("pdf-mo", "pdf-mo"),
        ("pdf-lt", "pdf-lt"),
        ("pdf-lb", "pdf-lb"),
        ("pdf-s", "pdf-so"),
        ("svg", "svg"),
        ("svg-d", "svg"),
        ("svg-do", "svg"),
        ("svg-l", "svg-lo"),
        ("svg-lo", "svg-lo"),
        ("svg-lb", "svg-lb"),
        ("svg-lt", "svg-lt"),
        ("png", "png"),
        ("png-d", "png"),
        ("png-l", "png-l"),
        ("jpg", "jpg"),
        ("jpg-d", "jpg"),
        ("jpg-s", "jpg-s"),
    ],
)
def test_parse_valid_round_trips(input_str: str, expected_str: str) -> None:
    spec = FormatSpec.parse(input_str)
    assert str(spec) == expected_str, f"parse({input_str!r}).__str__() = {str(spec)!r}, want {expected_str!r}"


# ---------------------------------------------------------------------------
# FormatSpec.parse — invalid inputs must raise InvalidInput
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    "bad_input",
    [
        "foo",         # unknown format
        "pdf-x",       # bad packaging char
        "pdf-dz",      # bad content char
        "png-o",       # bitmap with content qualifier (single char that's a content char)
        "jpg-l",       # jpg has no layered form
        "svg-m",       # svg has no multi-page form
        "",            # empty string
        "pdf-doo",     # qualifier too long
    ],
)
def test_parse_invalid_raises(bad_input: str) -> None:
    with pytest.raises(InvalidInput):
        FormatSpec.parse(bad_input)


# ---------------------------------------------------------------------------
# FormatSpec.from_extension
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    ("path", "expected_fmt"),
    [
        ("document.pdf", "pdf"),
        ("graphic.svg", "svg"),
        ("image.png", "png"),
        ("photo.jpg", "jpg"),
        ("photo.jpeg", "jpg"),
    ],
)
def test_from_extension_known(path: str, expected_fmt: str) -> None:
    spec = FormatSpec.from_extension(path)
    assert spec.format == expected_fmt


def test_from_extension_unknown_raises() -> None:
    with pytest.raises(InvalidInput):
        FormatSpec.from_extension("file.xyz")


def test_from_extension_path_object() -> None:
    spec = FormatSpec.from_extension(Path("out/result.svg"))
    assert spec.format == "svg"


# ---------------------------------------------------------------------------
# is_vector / is_bitmap
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("fmt,expected_vector,expected_bitmap", [
    ("pdf", True, False),
    ("svg", True, False),
    ("png", False, True),
    ("jpg", False, True),
])
def test_is_vector_bitmap(fmt: str, expected_vector: bool, expected_bitmap: bool) -> None:
    spec = FormatSpec.parse(fmt)
    assert spec.is_vector == expected_vector
    assert spec.is_bitmap == expected_bitmap


# ---------------------------------------------------------------------------
# FormatSpec field values after parse
# ---------------------------------------------------------------------------

def test_pdf_defaults_content_o() -> None:
    spec = FormatSpec.parse("pdf")
    assert spec.packaging == Packaging.D
    assert spec.content == Content.O


def test_svg_defaults_content_o() -> None:
    spec = FormatSpec.parse("svg")
    assert spec.content == Content.O


def test_png_content_is_none() -> None:
    spec = FormatSpec.parse("png")
    assert spec.content is None


def test_jpg_content_is_none() -> None:
    spec = FormatSpec.parse("jpg")
    assert spec.content is None


def test_pdf_mo_fields() -> None:
    spec = FormatSpec.parse("pdf-mo")
    assert spec.format == "pdf"
    assert spec.packaging == Packaging.M
    assert spec.content == Content.O


def test_svg_lt_fields() -> None:
    spec = FormatSpec.parse("svg-lt")
    assert spec.format == "svg"
    assert spec.packaging == Packaging.L
    assert spec.content == Content.T


# ---------------------------------------------------------------------------
# Hints.parse
# ---------------------------------------------------------------------------

def test_hints_parse_none_is_empty() -> None:
    h = Hints.parse(None)
    assert h.preferences == ()
    assert not h


def test_hints_parse_string() -> None:
    h = Hints.parse("re,mu")
    assert h.preferences == (Hint.RE, Hint.MU)
    assert bool(h)


def test_hints_parse_string_whitespace() -> None:
    h = Hints.parse(" re , mu ")
    assert h.preferences == (Hint.RE, Hint.MU)


def test_hints_parse_unknown_raises() -> None:
    with pytest.raises(InvalidInput):
        Hints.parse("bad")


def test_hints_parse_iterable_of_hints() -> None:
    h = Hints.parse([Hint.PK, Hint.AP])
    assert h.preferences == (Hint.PK, Hint.AP)


def test_hints_parse_iterable_of_strings() -> None:
    h = Hints.parse(["re", "pk"])
    assert h.preferences == (Hint.RE, Hint.PK)


def test_hints_parse_mixed_iterable() -> None:
    h = Hints.parse([Hint.MU, "pk"])
    assert h.preferences == (Hint.MU, Hint.PK)


# ---------------------------------------------------------------------------
# Hints.pick
# ---------------------------------------------------------------------------

def test_hints_pick_first_match() -> None:
    h = Hints.parse("re,mu,pk")
    result = h.pick([Hint.MU, Hint.PK])
    # re is not in candidates; mu comes first in preferences
    assert result == Hint.MU


def test_hints_pick_priority_order() -> None:
    h = Hints.parse("pk,re,mu")
    result = h.pick([Hint.RE, Hint.MU])
    # pk not in candidates; re comes before mu in preferences
    assert result == Hint.RE


def test_hints_pick_no_match_returns_none() -> None:
    h = Hints.parse("re")
    result = h.pick([Hint.MU, Hint.PK])
    assert result is None


def test_hints_pick_empty_preferences() -> None:
    h = Hints.parse(None)
    assert h.pick([Hint.RE, Hint.MU]) is None


# ---------------------------------------------------------------------------
# BackendFailure
# ---------------------------------------------------------------------------

def test_backend_failure_str() -> None:
    original = ValueError("disk full")
    err = BackendFailure("pymupdf", "pdf→png", original)
    assert str(err) == "[pymupdf] pdf→png failed: disk full"


def test_backend_failure_attrs() -> None:
    original = RuntimeError("oops")
    err = BackendFailure("pikepdf", "split", original)
    assert err.backend == "pikepdf"
    assert err.op == "split"
    assert err.original is original


def test_backend_failure_is_vexy_error() -> None:
    from vexy_pdfsvgpy.errors import VexyError
    err = BackendFailure("resvg", "svg→png", Exception("x"))
    assert isinstance(err, VexyError)


# ---------------------------------------------------------------------------
# this_file marker checks
# ---------------------------------------------------------------------------

def test_errors_has_this_file_marker() -> None:
    text = Path("src/vexy_pdfsvgpy/errors.py").read_text()
    assert "this_file:" in text


def test_types_has_this_file_marker() -> None:
    text = Path("src/vexy_pdfsvgpy/types.py").read_text()
    assert "this_file:" in text


def test_test_types_has_this_file_marker() -> None:
    text = Path("tests/test_types.py").read_text()
    assert "this_file:" in text
