from __future__ import annotations
# this_file: src/vexy_pdfsvgpy/backends/resvg_backend.py
"""resvg-py backend — SVG rasterization via the usvg/resvg Rust pipeline."""

import re
from pathlib import Path

BACKEND_NAME = "resvg"

_PT_ATTR_RE = re.compile(r'(\b(?:width|height))="([\d.]+)pt"')


def _ensure_parent(dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)


def _to_png_bytes(svg_path: Path | None, svg_string: str | None, width: int) -> bytes:
    """Call resvg_py, normalise return type to bytes."""
    import resvg_py

    kwargs: dict = {"width": width}
    if svg_path is not None:
        kwargs["svg_path"] = str(svg_path)
    else:
        kwargs["svg_string"] = svg_string

    result = resvg_py.svg_to_bytes(**kwargs)
    return bytes(result) if not isinstance(result, (bytes, bytearray)) else bytes(result)


def _render(src_path: Path | None, src_string: str | None, width: int) -> bytes:
    """Render SVG to PNG bytes, with pt-unit fallback on 'invalid size' errors."""
    try:
        return _to_png_bytes(src_path, src_string, width)
    except ValueError as e:
        if "invalid size" not in str(e).lower():
            raise RuntimeError(f"[resvg] render failed: {e}") from e
        # pt-unit fallback: rewrite width/height pt attributes to unitless px
        text = (
            src_path.read_text(encoding="utf-8", errors="replace")
            if src_path is not None
            else (src_string or "")
        )
        patched = _PT_ATTR_RE.sub(r'\1="\2"', text)
        try:
            return _to_png_bytes(None, patched, width)
        except Exception as e2:
            raise RuntimeError(f"[resvg] render (pt-fallback) failed: {e2}") from e2


def svg_to_png(src: Path, dst: Path, *, width: int = 2048) -> Path:
    """Render an SVG to PNG at the given pixel width.

    Calls resvg_py.svg_to_bytes(svg_path=..., width=...). If resvg raises
    ValueError containing 'invalid size' (SVGs with pt units in width/height),
    regex-patches ``(width|height)="N pt"`` → ``\\1="N"`` and retries once
    with svg_string=....
    """
    try:
        png = _render(src, None, width)
    except RuntimeError:
        raise
    except Exception as e:
        raise RuntimeError(f"[resvg] svg_to_png failed: {e}") from e
    _ensure_parent(dst)
    dst.write_bytes(png)
    return dst


def svg_to_png_bytes(svg_source: str | bytes | Path, *, width: int = 2048) -> bytes:
    """Return PNG bytes given an SVG as path, str, or bytes."""
    try:
        if isinstance(svg_source, Path):
            return _render(svg_source, None, width)
        if isinstance(svg_source, (bytes, bytearray)):
            text = svg_source.decode("utf-8", errors="replace")
            return _render(None, text, width)
        return _render(None, svg_source, width)
    except RuntimeError:
        raise
    except Exception as e:
        raise RuntimeError(f"[resvg] svg_to_png_bytes failed: {e}") from e
