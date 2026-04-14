from __future__ import annotations
# this_file: src/vexy_pdfsvgpy/backends/pypdf_backend.py
"""pypdf backend — pure-Python PDF split and merge."""

from pathlib import Path

BACKEND_NAME = "pypdf"


def split(src: Path, out_dir: Path, *, stem: str | None = None) -> list[Path]:
    """Split a PDF into one file per page. Returns list of output paths.

    Filenames: `{stem}-pypdf-page-{i+1:0{pad}d}.pdf` where `stem` defaults to
    `src.stem` and `pad = max(2, len(str(n_pages)))`.
    """
    try:
        from pypdf import PdfReader, PdfWriter
    except Exception as e:
        raise RuntimeError(f"[pypdf] split failed: {e}") from e

    out_dir.mkdir(parents=True, exist_ok=True)
    _stem = stem if stem is not None else src.stem

    try:
        reader = PdfReader(str(src))
        n = len(reader.pages)
        pad = max(2, len(str(n)))
        outputs: list[Path] = []
        for i, page in enumerate(reader.pages):
            writer = PdfWriter()
            writer.add_page(page)
            dst_i = out_dir / f"{_stem}-pypdf-page-{i + 1:0{pad}d}.pdf"
            with dst_i.open("wb") as fh:
                writer.write(fh)
            outputs.append(dst_i)
        return outputs
    except RuntimeError:
        raise
    except Exception as e:
        raise RuntimeError(f"[pypdf] split failed: {e}") from e


def merge(srcs: list[Path], dst: Path) -> Path:
    """Merge a list of PDFs into one. Preserves page order."""
    try:
        from pypdf import PdfReader, PdfWriter
    except Exception as e:
        raise RuntimeError(f"[pypdf] merge failed: {e}") from e

    dst.parent.mkdir(parents=True, exist_ok=True)

    try:
        writer = PdfWriter()
        for s in srcs:
            reader = PdfReader(str(s))
            for page in reader.pages:
                writer.add_page(page)
        with dst.open("wb") as fh:
            writer.write(fh)
        return dst
    except RuntimeError:
        raise
    except Exception as e:
        raise RuntimeError(f"[pypdf] merge failed: {e}") from e


def pdf_page_count(src: Path) -> int:
    """Return the number of pages in a PDF."""
    try:
        from pypdf import PdfReader
        return len(PdfReader(str(src)).pages)
    except Exception as e:
        raise RuntimeError(f"[pypdf] pdf_page_count failed: {e}") from e
