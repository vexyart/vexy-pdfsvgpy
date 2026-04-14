#!/usr/bin/env -S uv run -s
# /// script
# requires-python = ">=3.12"
# dependencies = ["vexy-pdfsvgpy"]
# ///
# this_file: examples/convert_coupon.py
"""Split a multi-page PDF, rasterize each page at 300dpi, re-merge into one PDF.

Run:
    uv run examples/convert_coupon.py
"""
from __future__ import annotations

import tempfile
from pathlib import Path

from rich.console import Console

from vexy_pdfsvgpy import convert
from vexy_pdfsvgpy.operations import reshape

console = Console()

ROOT = Path(__file__).resolve().parent.parent
TESTDATA = ROOT / "testdata"
SRC = TESTDATA / "fontlab_posters.pdf"


def main() -> int:
    if not SRC.exists():
        console.print(f"[red]Missing fixture:[/red] {SRC}")
        return 1
    with tempfile.TemporaryDirectory() as d:
        tmp = Path(d)
        # 1) Split into per-page PDFs
        pages = reshape.pages2docs_pdf(SRC, tmp / "split")
        console.print(f"[green]Split[/green] into {len(pages)} page(s)")

        # 2) Rasterize each page at 300dpi
        pngs: list[Path] = []
        for i, p in enumerate(pages, 1):
            png = tmp / f"page_{i:02d}.png"
            convert(input=str(p), output=str(png))
            pngs.append(png)
            console.print(f"  rasterized page {i}: {png.stat().st_size:,} B")

        # 3) Re-merge split PDFs
        merged = reshape.docs2pages_pdf(pages, tmp / "merged.pdf")
        console.print(f"[green]Merged[/green] back: {merged.stat().st_size:,} B")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
