from __future__ import annotations
# this_file: src/vexy_pdfsvgpy/backends/cairo_backend.py
"""CairoSVG backend."""

from pathlib import Path

BACKEND_NAME = "cairo"

def ensure_parent(p: Path) -> Path:
    p.parent.mkdir(parents=True, exist_ok=True)
    return p

def svg_to_png(src: Path, dst: Path, *, dpi: int = 300) -> Path:
    import cairosvg
    ensure_parent(dst)
    try:
        cairosvg.svg2png(url=str(src), write_to=str(dst), dpi=dpi)
        return dst
    except Exception as e:
        raise RuntimeError(f"[cairo] svg_to_png failed: {e}") from e

def svg_to_pdf(src: Path, dst: Path) -> Path:
    import cairosvg
    ensure_parent(dst)
    try:
        cairosvg.svg2pdf(url=str(src), write_to=str(dst))
        return dst
    except Exception as e:
        raise RuntimeError(f"[cairo] svg_to_pdf failed: {e}") from e
