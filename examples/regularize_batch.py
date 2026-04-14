#!/usr/bin/env -S uv run -s
# /// script
# requires-python = ">=3.12"
# dependencies = ["vexy-pdfsvgpy"]
# ///
# this_file: examples/regularize_batch.py
"""Regularize (canonicalize) every fixture in testdata/ and report sizes."""
from __future__ import annotations

import tempfile
from pathlib import Path

from rich.console import Console
from rich.table import Table

from vexy_pdfsvgpy.operations import regularize

console = Console()
ROOT = Path(__file__).resolve().parent.parent
TESTDATA = ROOT / "testdata"


def main() -> int:
    if not TESTDATA.exists():
        console.print(f"[red]Missing fixtures dir:[/red] {TESTDATA}")
        return 1
    table = Table(title="Regularize: size before → after")
    table.add_column("File", style="cyan")
    table.add_column("Ext", style="magenta")
    table.add_column("Before", justify="right", style="yellow")
    table.add_column("After", justify="right", style="green")
    with tempfile.TemporaryDirectory() as d:
        tmp = Path(d)
        for src in sorted(TESTDATA.iterdir()):
            ext = src.suffix.lower()
            if ext not in {".pdf", ".svg"}:
                continue
            dst = tmp / f"{src.stem}-norm{ext}"
            try:
                if ext == ".pdf":
                    regularize.regularize_pdf(src, dst)
                else:
                    regularize.regularize_svg(src, dst)
                before = src.stat().st_size
                after = dst.stat().st_size
                table.add_row(src.name, ext, f"{before:,}", f"{after:,}")
            except Exception as e:
                table.add_row(src.name, ext, "-", f"[red]{type(e).__name__}[/red]")
    console.print(table)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
