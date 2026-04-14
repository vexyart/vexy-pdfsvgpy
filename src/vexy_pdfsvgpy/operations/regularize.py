from __future__ import annotations
# this_file: src/vexy_pdfsvgpy/operations/regularize.py
"""Regularize — round-trip canonicalization of PDF and SVG files."""

from pathlib import Path
from typing import Literal


def regularize_pdf(
    src: Path,
    dst: Path,
    *,
    backend: Literal["pymupdf", "apple"] = "pymupdf",
) -> Path:
    """Canonicalize a PDF via round-trip through pymupdf (clean=True, deflate=True, garbage=4)
    or via Apple PDFKit on macOS with hint 'apple'."""
    try:
        if backend == "pymupdf":
            from ..backends import pymupdf_backend
            return pymupdf_backend.pdf_normalize(src, dst)
        if backend == "apple":
            from ..backends import apple_backend
            return apple_backend.pdf_normalize(src, dst)
        raise ValueError(f"unknown pdf backend: {backend}")
    except Exception as e:
        if str(e).startswith("[regularize]"):
            raise RuntimeError(str(e)) from e
        raise RuntimeError(f"[regularize] regularize_pdf failed: {e}") from e


def regularize_svg(
    src: Path,
    dst: Path,
    *,
    backend: Literal["pymupdf", "resvg"] = "pymupdf",
    width: int = 2048,
) -> Path:
    """Canonicalize an SVG.

    'pymupdf' round-trips through get_svg_image(text_as_path=True).
    'resvg' rasterizes to PNG then wraps the bitmap as a base64 <image> inside a minimal SVG
    (a raster-only canonicalization useful when the input has exotic features pymupdf can't round-trip).
    """
    try:
        if backend == "pymupdf":
            from ..backends import pymupdf_backend
            return pymupdf_backend.svg_normalize(src, dst)
        if backend == "resvg":
            return _regularize_svg_resvg(src, dst, width=width)
        raise ValueError(f"unknown svg backend: {backend}")
    except Exception as e:
        if str(e).startswith("[regularize]"):
            raise RuntimeError(str(e)) from e
        raise RuntimeError(f"[regularize] regularize_svg failed: {e}") from e


def _regularize_svg_resvg(src: Path, dst: Path, *, width: int) -> Path:
    """Raster-wrap canonicalization: render to PNG then embed as base64 in minimal SVG."""
    import base64

    from ..backends import resvg_backend

    png_path = dst.with_suffix(".tmp.png")
    try:
        resvg_backend.svg_to_png(src, png_path, width=width)
        from PIL import Image

        with Image.open(png_path) as img:
            w, h = img.size
        data = base64.b64encode(png_path.read_bytes()).decode("ascii")
    finally:
        png_path.unlink(missing_ok=True)

    svg = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<svg xmlns="http://www.w3.org/2000/svg" '
        'xmlns:xlink="http://www.w3.org/1999/xlink" '
        f'width="{w}" height="{h}" viewBox="0 0 {w} {h}">\n'
        f'  <image width="{w}" height="{h}" xlink:href="data:image/png;base64,{data}"/>\n'
        "</svg>\n"
    )
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(svg, encoding="utf-8")
    return dst
