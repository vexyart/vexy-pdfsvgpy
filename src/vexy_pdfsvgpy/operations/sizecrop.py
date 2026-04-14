from __future__ import annotations
# this_file: src/vexy_pdfsvgpy/operations/sizecrop.py
"""Size-and-crop operations — resolve --dim, --scale, margin alignment, --crop."""

from dataclasses import dataclass, field as dc_field
from pathlib import Path
from typing import Literal


DimSpec = Literal["none", "largest", "first", "last"] | str  # or "WxH"
ScaleMode = Literal["fit", "keep", "width", "height"] | int  # int for NNN percent
CropMode = Literal["all", "keep", "width", "height", "down"]


@dataclass(frozen=True, slots=True)
class SizeCropOptions:
    dim: DimSpec = "none"
    scale: ScaleMode = "fit"
    top: float | None = None    # percent; None means "auto"
    bottom: float | None = None
    left: float | None = None
    right: float | None = None
    crop: CropMode = "all"


def parse_dim(value: str) -> tuple[int, int] | None:
    """Parse a 'WxH' string into (W, H) pixels. Returns None for 'none'."""
    if value == "none":
        return None
    if "x" in value.lower():
        try:
            w_s, h_s = value.lower().split("x", 1)
            return (int(w_s), int(h_s))
        except ValueError as e:
            raise RuntimeError(f"[sizecrop] bad dim spec: {value!r}") from e
    raise RuntimeError(f"[sizecrop] bad dim spec: {value!r}")


def resolve_dim(sources: list[tuple[int, int]], dim: DimSpec) -> tuple[int, int] | None:
    """Pick a target (W, H) from a list of source dimensions based on dim mode."""
    if dim == "none" or not sources:
        return None
    if dim == "first":
        return sources[0]
    if dim == "last":
        return sources[-1]
    if dim == "largest":
        return max(sources, key=lambda wh: wh[0] * wh[1])
    assert isinstance(dim, str)
    return parse_dim(dim)


def compute_scale(
    source_wh: tuple[int, int],
    target_wh: tuple[int, int],
    mode: ScaleMode,
) -> float:
    """Return a scale factor mapping source -> target per mode.

    - 'fit' preserves aspect, fits within target (min of x/y ratios).
    - 'keep' returns 1.0.
    - 'width' fits width only.
    - 'height' fits height only.
    - integer N returns N/100.0.
    """
    if isinstance(mode, int):
        return mode / 100.0
    if mode == "keep":
        return 1.0
    sw, sh = source_wh
    tw, th = target_wh
    if mode == "fit":
        return min(tw / sw, th / sh)
    if mode == "width":
        return tw / sw
    if mode == "height":
        return th / sh
    raise RuntimeError(f"[sizecrop] unknown scale mode: {mode!r}")


def resolve_margins(
    top: float | None,
    bottom: float | None,
    left: float | None,
    right: float | None,
) -> tuple[float, float, float, float]:
    """Apply CSS-style auto-margin rules and return concrete (top, bottom, left, right) in 0..100.

    - If top given and bottom is None -> bottom = auto (0).
    - If left given and right is None -> right = auto (0).
    - If none are given -> all 0 (centered).
    """
    t = top if top is not None else 0.0
    b = bottom if bottom is not None else 0.0
    l = left if left is not None else 0.0
    r = right if right is not None else 0.0
    return (t, b, l, r)


def apply_sizecrop_pdf(src: Path, dst: Path, options: SizeCropOptions) -> Path:
    """Apply size-and-crop to a PDF via pymupdf.

    Opens the PDF, reads source page dimensions, resolves target dim, scale, margins,
    creates a new PDF with the target size, draws the scaled source into it at the
    resolved position. 'crop all' pads with whitespace to hit target exactly.
    """
    if options.dim == "none":
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_bytes(src.read_bytes())
        return dst
    try:
        import pymupdf

        src_doc = pymupdf.open(str(src))
        try:
            sources = [
                (int(src_doc[i].rect.width), int(src_doc[i].rect.height))
                for i in range(len(src_doc))
            ]
            target = resolve_dim(sources, options.dim)
            if target is None:
                dst.parent.mkdir(parents=True, exist_ok=True)
                dst.write_bytes(src.read_bytes())
                return dst
            tw, th = target
            out = pymupdf.open()
            for i, (sw, sh) in enumerate(sources):
                scale = compute_scale((sw, sh), (tw, th), options.scale)
                new_w = sw * scale
                new_h = sh * scale
                m_top, _m_bot, m_left, _m_right = resolve_margins(
                    options.top, options.bottom, options.left, options.right
                )
                # Centre by default (margins=0 → centre); margin is offset percentage
                x0 = (tw - new_w) * (m_left / 100.0 if options.left is not None else 0.5)
                y0 = (th - new_h) * (m_top / 100.0 if options.top is not None else 0.5)
                page = out.new_page(width=tw, height=th)
                rect = pymupdf.Rect(x0, y0, x0 + new_w, y0 + new_h)
                page.show_pdf_page(rect, src_doc, i)
            dst.parent.mkdir(parents=True, exist_ok=True)
            out.save(str(dst), garbage=4, deflate=True)
            out.close()
            return dst
        finally:
            src_doc.close()
    except RuntimeError:
        raise
    except Exception as e:
        raise RuntimeError(f"[sizecrop] apply_sizecrop_pdf failed: {e}") from e
