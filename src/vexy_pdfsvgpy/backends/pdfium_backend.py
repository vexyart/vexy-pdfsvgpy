from __future__ import annotations
# this_file: src/vexy_pdfsvgpy/backends/pdfium_backend.py
"""pypdfium2 backend — PDF rasterization."""

from pathlib import Path

BACKEND_NAME = "pdfium"


def ensure_parent(p: Path) -> Path:
    """Create parent directories for *p* if they don't exist."""
    p.parent.mkdir(parents=True, exist_ok=True)
    return p


def pdf_to_png(src: Path, dst: Path, *, page: int = 0, dpi: int = 300) -> Path:
    """Render a PDF page to PNG via pypdfium2.

    Uses ``pdf[page].render(scale=dpi/72)`` and saves via Pillow. Matches the
    demo script (external/pdfsvgpy_demo.py line 192-195).

    Args:
        src: Path to the source PDF file.
        dst: Destination PNG path.
        page: Zero-based page index to render.
        dpi: Output resolution in dots per inch.

    Returns:
        The resolved destination path.

    Raises:
        RuntimeError: Wraps any pypdfium2 or Pillow error with a ``[pdfium]`` prefix.
    """
    import pypdfium2 as pdfium

    src = Path(src)
    dst = Path(dst)
    ensure_parent(dst)
    pdf = pdfium.PdfDocument(str(src))
    try:
        bitmap = pdf[page].render(scale=dpi / 72)
        bitmap.to_pil().save(str(dst))
    except Exception as e:
        raise RuntimeError(f"[pdfium] pdf_to_png failed: {e}") from e
    finally:
        pdf.close()
    return dst


def pdf_page_count(src: Path) -> int:
    """Return the number of pages in a PDF.

    Args:
        src: Path to the PDF file.

    Returns:
        Total page count.

    Raises:
        RuntimeError: Wraps any pypdfium2 error with a ``[pdfium]`` prefix.
    """
    import pypdfium2 as pdfium

    src = Path(src)
    try:
        pdf = pdfium.PdfDocument(str(src))
    except Exception as e:
        raise RuntimeError(f"[pdfium] pdf_page_count failed: {e}") from e
    try:
        return len(pdf)
    finally:
        pdf.close()
