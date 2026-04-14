#!/usr/bin/env -S uv run -s
# /// script
# requires-python = ">=3.12"
# dependencies = ["vexy-pdfsvgpy"]
# ///
# this_file: examples/layer_stack.py
"""Stack multiple SVGs into a layered SVG and a layered PDF."""
from __future__ import annotations

import tempfile
from pathlib import Path

import pymupdf
from rich.console import Console

from vexy_pdfsvgpy import convert
from vexy_pdfsvgpy.operations import reshape

console = Console()
ROOT = Path(__file__).resolve().parent.parent
SRCS_SVG = [
    ROOT / "testdata" / "initial.svg",
    ROOT / "testdata" / "hello_glyphs.svg",
    ROOT / "testdata" / "svglogo.svg",
]


def main() -> int:
    missing = [p for p in SRCS_SVG if not p.exists()]
    if missing:
        console.print(f"[red]Missing fixtures:[/red] {missing}")
        return 1
    with tempfile.TemporaryDirectory() as d:
        tmp = Path(d)
        # 1) Stack SVGs as layered SVG
        layered_svg = reshape.docs2layers_svg(SRCS_SVG, tmp / "layered.svg")
        console.print(f"[green]Layered SVG:[/green] {layered_svg.stat().st_size:,} B")

        # 2) Convert each SVG to PDF first, then stack as OCG PDF
        pdfs = []
        for i, s in enumerate(SRCS_SVG):
            p = tmp / f"src_{i}.pdf"
            convert(input=str(s), output=str(p))
            pdfs.append(p)
        layered_pdf = reshape.docs2layers_pdf(
            pdfs,
            tmp / "layered.pdf",
            labels=["Initial", "Glyphs", "Logo"],
        )
        doc = pymupdf.open(str(layered_pdf))
        try:
            ocgs = doc.get_ocgs()
        finally:
            doc.close()
        console.print(f"[green]Layered PDF:[/green] {layered_pdf.stat().st_size:,} B")
        console.print(f"  OCGs: {list(ocg['name'] for ocg in ocgs.values())}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
