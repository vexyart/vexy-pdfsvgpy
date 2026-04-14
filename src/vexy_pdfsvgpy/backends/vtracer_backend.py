from __future__ import annotations
# this_file: src/vexy_pdfsvgpy/backends/vtracer_backend.py
"""vtracer backend — raster image vectorization (PNG/JPG → SVG)."""

from pathlib import Path
from typing import Literal

BACKEND_NAME = "vtracer"

ColorMode = Literal["color", "binary"]
Mode = Literal["spline", "polygon", "pixel"]


def trace(
    src: Path,
    dst: Path,
    *,
    colormode: ColorMode = "color",
    mode: Mode = "spline",
    filter_speckle: int = 4,
    color_precision: int = 6,
    layer_difference: int = 16,
    corner_threshold: int = 60,
    length_threshold: float = 4.0,
    max_iterations: int = 10,
    splice_threshold: int = 45,
    path_precision: int = 8,
) -> Path:
    """Vectorize a raster image into SVG via vtracer's Rust pipeline."""
    import vtracer

    dst.parent.mkdir(parents=True, exist_ok=True)
    try:
        vtracer.convert_image_to_svg_py(
            str(src),
            str(dst),
            colormode=colormode,
            mode=mode,
            filter_speckle=filter_speckle,
            color_precision=color_precision,
            layer_difference=layer_difference,
            corner_threshold=corner_threshold,
            length_threshold=length_threshold,
            max_iterations=max_iterations,
            splice_threshold=splice_threshold,
            path_precision=path_precision,
        )
    except BaseException as e:
        raise RuntimeError(f"[vtracer] trace failed: {e}") from e
    return dst
