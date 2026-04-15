from __future__ import annotations
# this_file: src/vexy_pdfsvgpy/backends/ghostscript_backend.py
"""Ghostscript backend."""

from pathlib import Path
import subprocess

BACKEND_NAME = "ghostscript"

def ensure_parent(p: Path) -> Path:
    p.parent.mkdir(parents=True, exist_ok=True)
    return p

def pdf_to_png(src: Path, dst: Path, *, page: int = 0, dpi: int = 300) -> Path:
    ensure_parent(dst)
    try:
        # Note: ghostscript python wrapper exists, or we can use subprocess
        # Since it's an extra, we assume the python package is installed
        import ghostscript
        args = [
            "gs",
            "-dSAFER",
            "-dBATCH",
            "-dNOPAUSE",
            f"-dFirstPage={page + 1}",
            f"-dLastPage={page + 1}",
            "-sDEVICE=png16m",
            f"-r{dpi}",
            f"-sOutputFile={dst}",
            str(src)
        ]
        ghostscript.Ghostscript(*args)
        return dst
    except Exception as e:
        raise RuntimeError(f"[ghostscript] pdf_to_png failed: {e}") from e

def pdf_normalize(src: Path, dst: Path, *, text_as: str | None = None) -> Path:
    ensure_parent(dst)
    try:
        import ghostscript
        args = [
            "gs",
            "-dSAFER",
            "-dBATCH",
            "-dNOPAUSE",
            "-sDEVICE=pdfwrite",
        ]
        if text_as == "paths":
            args.append("-dNoOutputFonts")
            
        args.extend([
            f"-sOutputFile={dst}",
            str(src)
        ])
        ghostscript.Ghostscript(*args)
        return dst
    except Exception as e:
        raise RuntimeError(f"[ghostscript] pdf_normalize failed: {e}") from e
