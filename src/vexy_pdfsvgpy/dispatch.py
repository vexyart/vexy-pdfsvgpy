from __future__ import annotations
# this_file: src/vexy_pdfsvgpy/dispatch.py
"""Capability dispatch — pick a backend function per operation + hints."""

from collections.abc import Callable
from dataclasses import dataclass
from enum import StrEnum
from typing import Any

from .errors import UnsupportedConversion
from .types import Hint, Hints


class Capability(StrEnum):
    PDF_TO_PNG = "pdf_to_png"
    PDF_TO_SVG = "pdf_to_svg"
    SVG_TO_PDF = "svg_to_pdf"
    SVG_TO_PNG = "svg_to_png"
    PDF_NORMALIZE = "pdf_normalize"
    SVG_NORMALIZE = "svg_normalize"
    PDF_SPLIT = "pdf_split"
    PDF_MERGE = "pdf_merge"
    PNG_TO_SVG_TRACE = "png_to_svg_trace"
    PNG_TO_SVG_WRAP = "png_to_svg_wrap"
    BITMAP_TO_PDF = "bitmap_to_pdf"
    PDF_PAGE_COUNT = "pdf_page_count"
    PDF_PAGE_SIZE = "pdf_page_size"


@dataclass(frozen=True, slots=True)
class BackendFn:
    name: str            # e.g. "pymupdf"
    hint: Hint           # e.g. Hint.MU
    func: Callable[..., Any]


def _load_table() -> dict[Capability, tuple[BackendFn, ...]]:
    """Build the dispatch table lazily so missing backends don't break import."""
    table: dict[Capability, list[BackendFn]] = {c: [] for c in Capability}

    # pymupdf — workhorse
    try:
        from .backends import pymupdf_backend as m
        table[Capability.PDF_TO_PNG].append(BackendFn("pymupdf", Hint.MU, m.pdf_to_png))
        table[Capability.PDF_TO_SVG].append(BackendFn("pymupdf", Hint.MU, m.pdf_to_svg))
        table[Capability.SVG_TO_PDF].append(BackendFn("pymupdf", Hint.MU, m.svg_to_pdf))
        table[Capability.SVG_TO_PNG].append(BackendFn("pymupdf", Hint.MU, m.svg_to_png))
        table[Capability.PDF_NORMALIZE].append(BackendFn("pymupdf", Hint.MU, m.pdf_normalize))
        table[Capability.SVG_NORMALIZE].append(BackendFn("pymupdf", Hint.MU, m.svg_normalize))
        table[Capability.PDF_PAGE_COUNT].append(BackendFn("pymupdf", Hint.MU, m.pdf_page_count))
        table[Capability.PDF_PAGE_SIZE].append(BackendFn("pymupdf", Hint.MU, m.pdf_page_size))
    except ImportError:
        pass

    # pypdfium2 — alternate PDF → PNG
    try:
        from .backends import pdfium_backend as pf
        table[Capability.PDF_TO_PNG].append(BackendFn("pdfium", Hint.MU, pf.pdf_to_png))
    except ImportError:
        pass

    # resvg — preferred SVG → PNG; inserted at FRONT
    try:
        from .backends import resvg_backend as r
        table[Capability.SVG_TO_PNG].insert(0, BackendFn("resvg", Hint.RE, r.svg_to_png))
    except ImportError:
        pass

    # pypdf — pure-Python split/merge
    try:
        from .backends import pypdf_backend as pp
        table[Capability.PDF_SPLIT].append(BackendFn("pypdf", Hint.PK, pp.split))
        table[Capability.PDF_MERGE].append(BackendFn("pypdf", Hint.PK, pp.merge))
    except ImportError:
        pass

    # pikepdf — lossless; merge inserted at FRONT (preferred over pypdf)
    try:
        from .backends import pikepdf_backend as pk
        table[Capability.PDF_SPLIT].append(BackendFn("pikepdf", Hint.PK, pk.split))
        table[Capability.PDF_MERGE].insert(0, BackendFn("pikepdf", Hint.PK, pk.merge))
    except ImportError:
        pass

    # vtracer — PNG → SVG trace
    try:
        from .backends import vtracer_backend as vt
        table[Capability.PNG_TO_SVG_TRACE].append(BackendFn("vtracer", Hint.RE, vt.trace))
    except ImportError:
        pass

    # wrap — PNG/JPG → SVG wrap, PNG/JPG → PDF
    try:
        from .backends import wrap_backend as w
        table[Capability.PNG_TO_SVG_WRAP].append(BackendFn("wrap", Hint.MU, w.png_to_svg))
        table[Capability.BITMAP_TO_PDF].append(BackendFn("wrap", Hint.MU, w.png_to_pdf))
    except ImportError:
        pass

    # apple — macOS; module imports cleanly, functions raise at call time on non-darwin
    try:
        from .backends import apple_backend as ap
        table[Capability.PDF_NORMALIZE].append(BackendFn("apple", Hint.AP, ap.pdf_normalize))
        table[Capability.PDF_TO_PNG].append(BackendFn("apple", Hint.AP, ap.pdf_to_png))
        table[Capability.PDF_SPLIT].append(BackendFn("apple", Hint.AP, ap.split))
        table[Capability.PDF_MERGE].append(BackendFn("apple", Hint.AP, ap.merge))
    except ImportError:
        pass

    return {c: tuple(v) for c, v in table.items()}


_TABLE: dict[Capability, tuple[BackendFn, ...]] | None = None


def capability_table() -> dict[Capability, tuple[BackendFn, ...]]:
    """Return the global dispatch table, building it on first call."""
    global _TABLE
    if _TABLE is None:
        _TABLE = _load_table()
    return _TABLE


def resolve(cap: Capability, hints: Hints | None = None) -> BackendFn:
    """Pick a backend for the given capability, honouring hint order."""
    candidates = capability_table().get(cap, ())
    if not candidates:
        raise UnsupportedConversion(f"no backend available for {cap.value}")
    if hints:
        for h in hints.preferences:
            for bf in candidates:
                if bf.hint is h:
                    return bf
    return candidates[0]
