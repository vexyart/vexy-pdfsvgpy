#!/usr/bin/env python3
"""Generate the small, committed PDF fixtures used by the test suite.

The real-world sample files live in the gitignored ``testdata/`` directory and
run to tens of megabytes — too large to commit, and unavailable in CI. These
synthetic stand-ins carry the same filenames and satisfy every structural
assumption the tests make (page counts, distinct page sizes, renderable vector
content) while staying a few kilobytes each.

Run from the repo root: ``uv run python tests/fixtures/_generate.py``
"""

# this_file: tests/fixtures/_generate.py
from __future__ import annotations

from pathlib import Path

import fitz  # PyMuPDF

HERE = Path(__file__).parent


def _draw(page: fitz.Page, label: str) -> None:
    """Put a little vector content on a page so it renders to non-zero pixels."""
    x0, y0, x1, y1 = page.rect.x0, page.rect.y0, page.rect.x1, page.rect.y1
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    page.draw_rect(fitz.Rect(x0 + 10, y0 + 10, x1 - 10, y1 - 10), color=(0, 0, 0), width=1.5)
    page.draw_line(
        fitz.Point(x0 + 10, y0 + 10), fitz.Point(x1 - 10, y1 - 10), color=(0.1, 0.1, 0.6), width=1
    )
    page.draw_circle(fitz.Point(cx, cy), min(x1 - x0, y1 - y0) / 4, color=(0.6, 0.1, 0.1), width=1)
    page.insert_text(fitz.Point(x0 + 16, y0 + 24), label, fontsize=11, color=(0, 0, 0))


def _make_pdf(path: Path, sizes: list[tuple[float, float]]) -> None:
    """Write a PDF with one page per (width, height) in ``sizes``."""
    doc = fitz.open()
    for i, (w, h) in enumerate(sizes):
        page = doc.new_page(width=w, height=h)
        _draw(page, f"{path.stem} p{i + 1}")
    doc.save(str(path), garbage=4, deflate=True)
    doc.close()


def main() -> None:
    # regularity.pdf: three pages of distinct area so "largest" is unambiguous
    # (400x300 > 300x300 > 200x300). Used across pipeline/backends/operations.
    _make_pdf(HERE / "regularity.pdf", [(200, 300), (400, 300), (300, 300)])
    # papercut.pdf: two pages so the specific-page render test actually runs.
    _make_pdf(HERE / "papercut.pdf", [(300, 400), (300, 400)])
    # fontlab_posters.pdf: three pages; a reshape test slices pages[:3].
    _make_pdf(HERE / "fontlab_posters.pdf", [(420, 594), (420, 594), (420, 594)])
    for p in sorted(HERE.glob("*.pdf")):
        print(f"{p.name}: {p.stat().st_size} bytes")


if __name__ == "__main__":
    main()
