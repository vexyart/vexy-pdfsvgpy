from __future__ import annotations
# this_file: src/vexy_pdfsvgpy/backends/wrap_backend.py
"""Wrap backend — embed bitmaps in minimal SVG/PDF containers.

This is the 'no-trace' fallback: instead of vectorizing, we wrap the
raster in a thin vector envelope. Useful when vtracer would be overkill
or produce garbage output (e.g. photographs).
"""

import base64
from pathlib import Path

BACKEND_NAME = "wrap"


def bitmap_to_svg(src: Path, dst: Path, *, mime: str | None = None) -> Path:
    """Generic: wrap any bitmap as a base64 <image> inside SVG.

    mime defaults to 'image/png' for .png, 'image/jpeg' for .jpg/.jpeg.
    """
    try:
        if mime is None:
            ext = src.suffix.lower()
            mime = {
                ".png": "image/png",
                ".jpg": "image/jpeg",
                ".jpeg": "image/jpeg",
            }.get(ext)
            if mime is None:
                raise RuntimeError(f"[wrap] unknown bitmap ext: {ext}")
        from PIL import Image

        with Image.open(src) as img:
            w, h = img.size
        data = base64.b64encode(src.read_bytes()).decode("ascii")
        svg = (
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            '<svg xmlns="http://www.w3.org/2000/svg" '
            'xmlns:xlink="http://www.w3.org/1999/xlink" '
            f'width="{w}" height="{h}" viewBox="0 0 {w} {h}">\n'
            f'  <image width="{w}" height="{h}" xlink:href="data:{mime};base64,{data}"/>\n'
            "</svg>\n"
        )
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_text(svg, encoding="utf-8")
        return dst
    except RuntimeError:
        raise
    except Exception as e:
        raise RuntimeError(f"[wrap] bitmap_to_svg failed: {e}") from e


def png_to_svg(src: Path, dst: Path) -> Path:
    """Wrap a PNG as a base64 <image> inside a minimal SVG."""
    return bitmap_to_svg(src, dst, mime="image/png")


def jpg_to_svg(src: Path, dst: Path) -> Path:
    """Wrap a JPG as a base64 <image> inside a minimal SVG."""
    return bitmap_to_svg(src, dst, mime="image/jpeg")


def png_to_pdf(src: Path, dst: Path) -> Path:
    """Wrap a PNG into a PDF via pymupdf direct open."""
    try:
        import pymupdf

        doc = pymupdf.open(str(src))
        try:
            pdf_bytes = doc.convert_to_pdf()
        finally:
            doc.close()
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_bytes(pdf_bytes)
        return dst
    except Exception as e:
        raise RuntimeError(f"[wrap] png_to_pdf failed: {e}") from e


def jpg_to_pdf(src: Path, dst: Path) -> Path:
    """Wrap a JPG into a PDF via pymupdf direct open."""
    try:
        import pymupdf

        doc = pymupdf.open(str(src))
        try:
            pdf_bytes = doc.convert_to_pdf()
        finally:
            doc.close()
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_bytes(pdf_bytes)
        return dst
    except Exception as e:
        raise RuntimeError(f"[wrap] jpg_to_pdf failed: {e}") from e
