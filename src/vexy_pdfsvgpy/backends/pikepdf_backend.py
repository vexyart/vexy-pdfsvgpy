from __future__ import annotations
# this_file: src/vexy_pdfsvgpy/backends/pikepdf_backend.py
"""pikepdf backend — lossless PDF split, merge, and page overlay."""

from pathlib import Path

BACKEND_NAME = "pikepdf"


def _ensure_parent(dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)


def split(src: Path, out_dir: Path, *, stem: str | None = None) -> list[Path]:
    """Split a PDF into one file per page. Returns list of output paths.

    Filenames: `{stem}-pikepdf-page-{i+1:0{pad}d}.pdf` where `stem` defaults
    to `src.stem` and `pad = max(2, len(str(n_pages)))`.
    """
    try:
        import pikepdf
    except Exception as e:
        raise RuntimeError(f"[pikepdf] split failed: {e}") from e

    out_dir.mkdir(parents=True, exist_ok=True)
    _stem = stem if stem is not None else src.stem

    try:
        pdf = pikepdf.open(str(src))
        try:
            n = len(pdf.pages)
            pad = max(2, len(str(n)))
            outputs: list[Path] = []
            for i, page in enumerate(pdf.pages):
                one = pikepdf.Pdf.new()
                one.pages.append(page)
                dst_i = out_dir / f"{_stem}-pikepdf-page-{i + 1:0{pad}d}.pdf"
                one.save(str(dst_i))
                one.close()
                outputs.append(dst_i)
            return outputs
        finally:
            pdf.close()
    except RuntimeError:
        raise
    except Exception as e:
        raise RuntimeError(f"[pikepdf] split failed: {e}") from e


def merge(srcs: list[Path], dst: Path) -> Path:
    """Merge a list of PDFs into one. Source PDFs stay open until save().

    pikepdf pages are referenced (not eagerly copied), so sources must remain
    open until `merged.save()` completes.
    """
    try:
        import pikepdf
    except Exception as e:
        raise RuntimeError(f"[pikepdf] merge failed: {e}") from e

    _ensure_parent(dst)

    merged = pikepdf.Pdf.new()
    opened: list[pikepdf.Pdf] = []
    try:
        for s in srcs:
            one = pikepdf.open(str(s))
            opened.append(one)
            merged.pages.extend(one.pages)
        merged.save(str(dst))
        return dst
    except RuntimeError:
        raise
    except Exception as e:
        raise RuntimeError(f"[pikepdf] merge failed: {e}") from e
    finally:
        for o in opened:
            o.close()
        merged.close()


def overlay_pages(base: Path, overlays: list[Path], dst: Path) -> Path:
    """Stack overlay PDFs onto page 0 of base using Form-XObject overlay.

    Each overlay's first page is composited onto the base page's mediabox.
    The result is written to `dst`; base and all overlays are lossless.
    """
    try:
        import pikepdf
        from pikepdf import Page, Pdf, Rectangle
    except Exception as e:
        raise RuntimeError(f"[pikepdf] overlay_pages failed: {e}") from e

    _ensure_parent(dst)

    base_pdf = Pdf.open(str(base))
    overlay_pdfs: list[Pdf] = []
    try:
        dest = Page(base_pdf.pages[0])
        rect = Rectangle(*dest.mediabox)
        for ov_path in overlays:
            ov_pdf = Pdf.open(str(ov_path))
            overlay_pdfs.append(ov_pdf)
            dest.add_overlay(ov_pdf.pages[0], rect)
        base_pdf.save(str(dst))
        return dst
    except RuntimeError:
        raise
    except Exception as e:
        raise RuntimeError(f"[pikepdf] overlay_pages failed: {e}") from e
    finally:
        for o in overlay_pdfs:
            o.close()
        base_pdf.close()


def pdf_page_count(src: Path) -> int:
    """Return the number of pages in a PDF."""
    try:
        import pikepdf
        pdf = pikepdf.open(str(src))
        try:
            return len(pdf.pages)
        finally:
            pdf.close()
    except RuntimeError:
        raise
    except Exception as e:
        raise RuntimeError(f"[pikepdf] pdf_page_count failed: {e}") from e
