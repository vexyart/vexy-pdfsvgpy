from __future__ import annotations
# this_file: src/vexy_pdfsvgpy/operations/color.py
"""Color operations — gray, invert, vivid, bright, contrast, backdrop."""

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class ColorOptions:
    gray: bool = False
    invert: bool = False
    vivid: float | None = None      # 0.0 = no change, positive saturates
    bright: float | None = None     # -100..100; positive brightens
    contrast: float | None = None   # -100..100; positive contrasts
    backdrop: str | None = None     # "#rrggbb", "#rrggbbaa", "white", "black", "dominant"


NAMED_COLORS: dict[str, tuple[int, int, int, int]] = {
    "white": (255, 255, 255, 255),
    "black": (0, 0, 0, 255),
    "red": (255, 0, 0, 255),
    "green": (0, 255, 0, 255),
    "blue": (0, 0, 255, 255),
}


def parse_color(
    s: str,
    ref_image: Path | None = None,
) -> tuple[int, int, int, int]:
    """Return (r, g, b, a) 0..255. Supports #rrggbb, #rrggbbaa, named colors,
    and 'dominant' (samples ref_image for the most-frequent pixel)."""
    s_low = s.lower()
    if s_low == "dominant":
        if ref_image is None:
            raise RuntimeError("[color] 'dominant' requires ref_image")
        from PIL import Image

        with Image.open(ref_image).convert("RGBA") as img:
            small = img.resize((64, 64))
            counts: dict[tuple[int, int, int, int], int] = {}
            for p in small.getdata():
                counts[p] = counts.get(p, 0) + 1  # type: ignore[index]
        return max(counts.items(), key=lambda kv: kv[1])[0]
    if s_low in NAMED_COLORS:
        return NAMED_COLORS[s_low]
    if s.startswith("#"):
        h = s[1:]
        if len(h) == 6:
            r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
            return (r, g, b, 255)
        if len(h) == 8:
            r, g, b, a = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), int(h[6:8], 16)
            return (r, g, b, a)
    raise RuntimeError(f"[color] bad color spec: {s!r}")


def apply_color_bitmap(src: Path, dst: Path, options: ColorOptions) -> Path:
    """Apply color ops to a bitmap file via Pillow. src/dst must be .png or .jpg."""
    try:
        from PIL import Image, ImageEnhance, ImageOps

        with Image.open(src).convert("RGBA") as img:
            # backdrop first: composite source onto solid background
            if options.backdrop:
                color = parse_color(options.backdrop, ref_image=src)
                bg = Image.new("RGBA", img.size, color)
                img = Image.alpha_composite(bg, img)
            # gray
            if options.gray:
                alpha = img.split()[-1]
                gray = ImageOps.grayscale(img).convert("RGBA")
                gray.putalpha(alpha)
                img = gray
            # invert (preserve alpha)
            if options.invert:
                r, g, b, a = img.split()
                rgb = Image.merge("RGB", (r, g, b))
                inv = ImageOps.invert(rgb)
                r2, g2, b2 = inv.split()
                img = Image.merge("RGBA", (r2, g2, b2, a))
            # vivid = saturation enhancement (1.0 = unchanged)
            if options.vivid is not None:
                img = ImageEnhance.Color(img).enhance(1.0 + options.vivid)
            # bright: -100..100 maps to 0.0..2.0 multiplier
            if options.bright is not None:
                img = ImageEnhance.Brightness(img).enhance(1.0 + options.bright / 100.0)
            # contrast: same -100..100 scale
            if options.contrast is not None:
                img = ImageEnhance.Contrast(img).enhance(1.0 + options.contrast / 100.0)
            dst.parent.mkdir(parents=True, exist_ok=True)
            if dst.suffix.lower() in (".jpg", ".jpeg"):
                img.convert("RGB").save(dst, "JPEG", quality=90)
            else:
                img.save(dst, "PNG")
            return dst
    except RuntimeError:
        raise
    except Exception as e:
        raise RuntimeError(f"[color] apply_color_bitmap failed: {e}") from e
