from __future__ import annotations

# this_file: tests/test_paths.py

"""Tests for src/vexy_pdfsvgpy/paths.py"""

from pathlib import Path

import pytest

from vexy_pdfsvgpy.paths import ensure_parent, parse_scale_suffix, render_output


# ---------------------------------------------------------------------------
# render_output — basic placeholder substitution
# ---------------------------------------------------------------------------


def test_render_stem_ext() -> None:
    result = render_output("out/{stem}.{ext}", stem="logo", page=1, ext="png")
    assert result == Path("out/logo.png"), result


def test_render_backend_scale() -> None:
    # scale already carries the '@' prefix (e.g. "@2048px"), so the template
    # must NOT include a literal '@' before {scale}.
    result = render_output(
        "out/{stem}-{backend}{scale}.{ext}",
        stem="logo",
        page=1,
        backend="resvg",
        scale="@2048px",
        ext="png",
    )
    assert result == Path("out/logo-resvg@2048px.png"), result


# ---------------------------------------------------------------------------
# Auto-pagination
# ---------------------------------------------------------------------------


def test_autopagination_pad2() -> None:
    """total_pages=10 → pad=2, page 3 → -p03."""
    result = render_output(
        "out/{stem}.{ext}", stem="doc", page=3, total_pages=10, ext="pdf"
    )
    assert result == Path("out/doc-p03.pdf"), result


def test_autopagination_pad3() -> None:
    """total_pages=100 + page=5 → -p005."""
    result = render_output(
        "out/{stem}.{ext}", stem="doc", page=5, total_pages=100, ext="pdf"
    )
    assert result == Path("out/doc-p005.pdf"), result


def test_autopagination_single_page_no_suffix() -> None:
    """total_pages=1: no auto-pagination even without {page}."""
    result = render_output("out/{stem}.{ext}", stem="doc", page=1, total_pages=1, ext="pdf")
    assert result == Path("out/doc.pdf"), result


# ---------------------------------------------------------------------------
# Explicit {page} placeholder suppresses auto-pagination
# ---------------------------------------------------------------------------


def test_explicit_page_suppresses_autopagination() -> None:
    result = render_output(
        "{stem}-{page:03d}.{ext}", stem="doc", page=3, total_pages=10, ext="pdf"
    )
    assert result == Path("doc-003.pdf"), result


def test_explicit_page_plain_suppresses_autopagination() -> None:
    result = render_output(
        "{stem}-{page}.{ext}", stem="doc", page=7, total_pages=50, ext="svg"
    )
    assert result == Path("doc-7.svg"), result


# ---------------------------------------------------------------------------
# Error cases
# ---------------------------------------------------------------------------


def test_unknown_placeholder_raises() -> None:
    with pytest.raises(ValueError, match="unknown"):
        render_output("{stem}-{unknown}.{ext}", stem="doc", page=1, ext="png")


def test_empty_stem_raises() -> None:
    with pytest.raises(ValueError, match="stem"):
        render_output("{stem}.{ext}", stem="", page=1, ext="png")


def test_empty_ext_raises() -> None:
    with pytest.raises(ValueError, match="ext"):
        render_output("{stem}.{ext}", stem="doc", page=1, ext="")


# ---------------------------------------------------------------------------
# No extension in template → append .{ext}
# ---------------------------------------------------------------------------


def test_no_extension_appended() -> None:
    result = render_output("{stem}", stem="output", page=1, ext="png")
    assert result == Path("output.png"), result


def test_no_extension_with_autopagination() -> None:
    """No extension + multi-page: pagination comes before the appended ext."""
    result = render_output("{stem}", stem="doc", page=2, total_pages=5, ext="png")
    # Should be doc-p02.png
    assert result == Path("doc-p02.png"), result


# ---------------------------------------------------------------------------
# parse_scale_suffix
# ---------------------------------------------------------------------------


def test_parse_scale_width() -> None:
    assert parse_scale_suffix(2048, None) == "@2048px"


def test_parse_scale_dpi() -> None:
    assert parse_scale_suffix(None, 300) == "@300dpi"


def test_parse_scale_none() -> None:
    assert parse_scale_suffix(None, None) == ""


def test_parse_scale_width_takes_priority() -> None:
    """width wins when both are given."""
    assert parse_scale_suffix(1024, 300) == "@1024px"


# ---------------------------------------------------------------------------
# ensure_parent
# ---------------------------------------------------------------------------


def test_ensure_parent_creates_dir(tmp_path: Path) -> None:
    target = tmp_path / "deep" / "nested" / "file.png"
    returned = ensure_parent(target)
    assert returned == target, "should return the original path"
    assert target.parent.is_dir(), "parent directory should have been created"


def test_ensure_parent_existing_dir_is_noop(tmp_path: Path) -> None:
    target = tmp_path / "file.png"
    ensure_parent(target)  # parent = tmp_path, already exists
    assert tmp_path.is_dir()


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------


def test_ext_leading_dot_stripped() -> None:
    """Passing ext='.png' (with dot) should not double the dot."""
    result = render_output("{stem}.{ext}", stem="img", page=1, ext=".png")
    assert result == Path("img.png"), result


def test_path_object_template() -> None:
    """template may be a Path object."""
    result = render_output(
        Path("out/{stem}.{ext}"), stem="logo", page=1, ext="svg"
    )
    assert result == Path("out/logo.svg"), result


def test_index_placeholder() -> None:
    result = render_output("{stem}-{index}.{ext}", stem="item", page=1, index=42, ext="png")
    assert result == Path("item-42.png"), result
