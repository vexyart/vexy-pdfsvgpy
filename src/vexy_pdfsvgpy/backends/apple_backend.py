from __future__ import annotations
# this_file: src/vexy_pdfsvgpy/backends/apple_backend.py
"""Apple PDFKit + CoreGraphics backend (macOS only)."""

import sys
from pathlib import Path

BACKEND_NAME = "apple"

IS_DARWIN = sys.platform == "darwin"


def _require_darwin(op: str) -> None:
    if not IS_DARWIN:
        raise RuntimeError(f"[apple] {op} unsupported on {sys.platform}")


def _ensure_parent(dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)


def pdf_page_count(src: Path) -> int:
    """Return the number of pages in a PDF via PDFKit."""
    _require_darwin("pdf_page_count")
    try:
        from Foundation import NSURL
        from Quartz import PDFDocument

        url = NSURL.fileURLWithPath_(str(src))
        doc = PDFDocument.alloc().initWithURL_(url)
        if doc is None:
            raise RuntimeError(f"[apple] PDFKit could not open {src}")
        return doc.pageCount()
    except RuntimeError:
        raise
    except Exception as e:
        raise RuntimeError(f"[apple] pdf_page_count failed: {e}") from e


def pdf_normalize(src: Path, dst: Path) -> Path:
    """Re-emit a PDF through PDFKit (normalize/repair)."""
    _require_darwin("pdf_normalize")
    _ensure_parent(dst)
    try:
        from Foundation import NSURL
        from Quartz import PDFDocument

        url = NSURL.fileURLWithPath_(str(src))
        doc = PDFDocument.alloc().initWithURL_(url)
        if doc is None:
            raise RuntimeError(f"[apple] PDFKit could not open {src}")
        if not doc.writeToFile_(str(dst)):
            raise RuntimeError(f"[apple] PDFKit write failed: {dst}")
        return dst
    except RuntimeError:
        raise
    except Exception as e:
        raise RuntimeError(f"[apple] pdf_normalize failed: {e}") from e


def split(src: Path, out_dir: Path, *, stem: str | None = None) -> list[Path]:
    """Split a PDF into one file per page using PDFKit."""
    _require_darwin("split")
    out_dir.mkdir(parents=True, exist_ok=True)
    _stem = stem if stem is not None else src.stem
    try:
        from Foundation import NSURL
        from Quartz import PDFDocument

        url = NSURL.fileURLWithPath_(str(src))
        doc = PDFDocument.alloc().initWithURL_(url)
        if doc is None:
            raise RuntimeError(f"[apple] could not open {src}")
        n = doc.pageCount()
        pad = max(2, len(str(n)))
        outputs: list[Path] = []
        for i in range(n):
            page = doc.pageAtIndex_(i)
            one = PDFDocument.alloc().init()
            one.insertPage_atIndex_(page, 0)
            dst_i = out_dir / f"{_stem}-apple-page-{i + 1:0{pad}d}.pdf"
            if not one.writeToFile_(str(dst_i)):
                raise RuntimeError(f"[apple] write failed: {dst_i}")
            outputs.append(dst_i)
        return outputs
    except RuntimeError:
        raise
    except Exception as e:
        raise RuntimeError(f"[apple] split failed: {e}") from e


def merge(srcs: list[Path], dst: Path) -> Path:
    """Merge PDFs into one using PDFKit."""
    _require_darwin("merge")
    _ensure_parent(dst)
    try:
        from Foundation import NSURL
        from Quartz import PDFDocument

        merged = PDFDocument.alloc().init()
        insert_at = 0
        for s in srcs:
            url = NSURL.fileURLWithPath_(str(s))
            doc = PDFDocument.alloc().initWithURL_(url)
            if doc is None:
                raise RuntimeError(f"[apple] could not open {s}")
            for i in range(doc.pageCount()):
                merged.insertPage_atIndex_(doc.pageAtIndex_(i), insert_at)
                insert_at += 1
        if not merged.writeToFile_(str(dst)):
            raise RuntimeError(f"[apple] write failed: {dst}")
        return dst
    except RuntimeError:
        raise
    except Exception as e:
        raise RuntimeError(f"[apple] merge failed: {e}") from e


def pdf_to_png(src: Path, dst: Path, *, page: int = 0, width: int = 2048) -> Path:
    """Rasterize a PDF page to PNG via CoreGraphics."""
    _require_darwin("pdf_to_png")
    _ensure_parent(dst)
    try:
        import Quartz
        from Foundation import NSURL

        url = NSURL.fileURLWithPath_(str(src))
        pdf = Quartz.CGPDFDocumentCreateWithURL(url)
        if pdf is None:
            raise RuntimeError(f"[apple] CGPDFDocument open failed: {src}")
        pg = Quartz.CGPDFDocumentGetPage(pdf, page + 1)  # 1-indexed
        if pg is None:
            raise RuntimeError(f"[apple] page {page} not found in {src}")
        media = Quartz.CGPDFPageGetBoxRect(pg, Quartz.kCGPDFMediaBox)
        if media.size.width <= 0 or media.size.height <= 0:
            raise RuntimeError("[apple] invalid media box")
        scale = width / media.size.width
        w = int(round(media.size.width * scale))
        h = int(round(media.size.height * scale))
        cs = Quartz.CGColorSpaceCreateDeviceRGB()
        ctx = Quartz.CGBitmapContextCreate(
            None, w, h, 8, 0, cs, Quartz.kCGImageAlphaPremultipliedLast
        )
        if ctx is None:
            raise RuntimeError("[apple] CGBitmapContextCreate failed")
        Quartz.CGContextSetRGBFillColor(ctx, 1.0, 1.0, 1.0, 1.0)
        Quartz.CGContextFillRect(ctx, Quartz.CGRectMake(0, 0, w, h))
        Quartz.CGContextTranslateCTM(ctx, -media.origin.x * scale, -media.origin.y * scale)
        Quartz.CGContextScaleCTM(ctx, scale, scale)
        Quartz.CGContextDrawPDFPage(ctx, pg)
        img = Quartz.CGBitmapContextCreateImage(ctx)
        if img is None:
            raise RuntimeError("[apple] CGBitmapContextCreateImage failed")
        out_url = NSURL.fileURLWithPath_(str(dst))
        dest = Quartz.CGImageDestinationCreateWithURL(out_url, "public.png", 1, None)
        if dest is None:
            raise RuntimeError("[apple] CGImageDestinationCreateWithURL failed")
        Quartz.CGImageDestinationAddImage(dest, img, None)
        if not Quartz.CGImageDestinationFinalize(dest):
            raise RuntimeError("[apple] CGImageDestinationFinalize failed")
        return dst
    except RuntimeError:
        raise
    except Exception as e:
        raise RuntimeError(f"[apple] pdf_to_png failed: {e}") from e
