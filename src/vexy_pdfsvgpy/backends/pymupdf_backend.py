from __future__ import annotations

# this_file: src/vexy_pdfsvgpy/backends/pymupdf_backend.py

from pathlib import Path

import pymupdf

BACKEND_NAME = "pymupdf"


def _ensure_parent(dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)


def _open(src: Path, op: str) -> pymupdf.Document:
    """Open a document, wrapping errors with backend prefix."""
    try:
        return pymupdf.open(str(src))
    except Exception as e:
        raise RuntimeError(f"[pymupdf] {op} failed: {e}") from e


def pdf_to_png(src: Path, dst: Path, *, page: int = 0, dpi: int = 300, alpha: bool = False) -> Path:
    """Render one PDF page to PNG."""
    _ensure_parent(dst)
    doc = _open(src, "pdf_to_png")
    try:
        pix = doc[page].get_pixmap(dpi=dpi, alpha=alpha)
        pix.save(str(dst))
    except RuntimeError:
        raise
    except Exception as e:
        raise RuntimeError(f"[pymupdf] pdf_to_png failed: {e}") from e
    finally:
        doc.close()
    return dst


def pdf_to_svg(src: Path, dst: Path, *, page: int = 0, text_as_path: bool = True) -> Path:
    """Render one PDF page to SVG."""
    _ensure_parent(dst)
    doc = _open(src, "pdf_to_svg")
    try:
        svg = doc[page].get_svg_image(text_as_path=text_as_path)
        dst.write_text(svg, encoding="utf-8")
    except RuntimeError:
        raise
    except Exception as e:
        raise RuntimeError(f"[pymupdf] pdf_to_svg failed: {e}") from e
    finally:
        doc.close()
    return dst


def svg_to_pdf(src: Path, dst: Path) -> Path:
    """Convert SVG to PDF via pymupdf convert_to_pdf()."""
    _ensure_parent(dst)
    doc = _open(src, "svg_to_pdf")
    try:
        pdf_bytes = doc.convert_to_pdf()
        dst.write_bytes(pdf_bytes)
    except RuntimeError:
        raise
    except Exception as e:
        raise RuntimeError(f"[pymupdf] svg_to_pdf failed: {e}") from e
    finally:
        doc.close()
    return dst


def svg_to_png(src: Path, dst: Path, *, dpi: int = 300, alpha: bool = True) -> Path:
    """Render SVG to PNG."""
    _ensure_parent(dst)
    doc = _open(src, "svg_to_png")
    try:
        pix = doc[0].get_pixmap(dpi=dpi, alpha=alpha)
        pix.save(str(dst))
    except RuntimeError:
        raise
    except Exception as e:
        raise RuntimeError(f"[pymupdf] svg_to_png failed: {e}") from e
    finally:
        doc.close()
    return dst


def pdf_normalize(src: Path, dst: Path) -> Path:
    """Normalize PDF: clean, deflate, deduplicate objects."""
    _ensure_parent(dst)
    doc = _open(src, "pdf_normalize")
    try:
        doc.save(str(dst), clean=True, deflate=True, garbage=4)
    except RuntimeError:
        raise
    except Exception as e:
        raise RuntimeError(f"[pymupdf] pdf_normalize failed: {e}") from e
    finally:
        doc.close()
    return dst


def svg_normalize(src: Path, dst: Path, *, page: int = 0, text_as_path: bool = True) -> Path:
    """Normalize SVG via pymupdf round-trip: open SVG, re-emit as SVG."""
    _ensure_parent(dst)
    doc = _open(src, "svg_normalize")
    try:
        svg = doc[page].get_svg_image(text_as_path=text_as_path)
        dst.write_text(svg, encoding="utf-8")
    except RuntimeError:
        raise
    except Exception as e:
        raise RuntimeError(f"[pymupdf] svg_normalize failed: {e}") from e
    finally:
        doc.close()
    return dst


def pdf_page_count(src: Path) -> int:
    """Return number of pages in a PDF."""
    doc = _open(src, "pdf_page_count")
    try:
        return len(doc)
    except RuntimeError:
        raise
    except Exception as e:
        raise RuntimeError(f"[pymupdf] pdf_page_count failed: {e}") from e
    finally:
        doc.close()


def pdf_page_size(src: Path, page: int = 0) -> tuple[float, float]:
    """Return (width, height) in points for the given page."""
    doc = _open(src, "pdf_page_size")
    try:
        rect = doc[page].rect
        return (rect.width, rect.height)
    except RuntimeError:
        raise
    except Exception as e:
        raise RuntimeError(f"[pymupdf] pdf_page_size failed: {e}") from e
    finally:
        doc.close()
