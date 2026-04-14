#!/usr/bin/env -S uv run -s
# /// script
# requires-python = ">=3.12"
# dependencies = ["vexy-pdfsvgpy"]
# ///
# this_file: examples/trace_logo.py
"""Rasterize an SVG logo, then vectorize the result via vtracer."""
from __future__ import annotations

import tempfile
from pathlib import Path

from rich.console import Console
from rich.table import Table

from vexy_pdfsvgpy.backends import resvg_backend, vtracer_backend

console = Console()
ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "testdata" / "svglogo.svg"


def main() -> int:
    if not SRC.exists():
        console.print(f"[red]Missing fixture:[/red] {SRC}")
        return 1
    with tempfile.TemporaryDirectory() as d:
        tmp = Path(d)
        raster = tmp / "logo.png"
        resvg_backend.svg_to_png(SRC, raster, width=1024)
        traced = tmp / "logo_traced.svg"
        vtracer_backend.trace(raster, traced)
        table = Table(title="SVG → PNG → SVG round-trip")
        table.add_column("Step", style="cyan")
        table.add_column("File", style="magenta")
        table.add_column("Size", justify="right", style="green")
        table.add_row("original svg", str(SRC.name), f"{SRC.stat().st_size:,}")
        table.add_row("rasterized png", str(raster.name), f"{raster.stat().st_size:,}")
        table.add_row("traced svg", str(traced.name), f"{traced.stat().st_size:,}")
        console.print(table)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
