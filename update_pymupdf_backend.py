import re

with open('src/vexy_pdfsvgpy/backends/pymupdf_backend.py', 'r') as f:
    content = f.read()

# Make text_as_path dynamic based on text_as argument if provided
pdf_svg_regex = r"def pdf_to_svg\(src: Path, dst: Path, \*, page: int = 0, text_as_path: bool = True\) -> Path:.*?return dst"
pdf_svg_new = """def pdf_to_svg(src: Path, dst: Path, *, page: int = 0, text_as: str | None = None) -> Path:
    \"\"\"Render one PDF page to SVG.\"\"\"
    _ensure_parent(dst)
    doc = _open(src, "pdf_to_svg")
    try:
        # According to issue #102:
        # "text": preserve text (text_as_path=False)
        # "paths": always convert to paths (text_as_path=True)
        # "fonts": default (text_as_path=False)
        # Wait, for pymupdf, getting text requires text_as_path=False.
        # But wait, original code was text_as_path=True.
        # So "paths" -> text_as_path=True
        # "text" -> text_as_path=False
        # "fonts" -> text_as_path=False (pymupdf might handle embedded fonts depending on what gets serialized)
        
        # We will map it this way:
        is_text_as_path = True
        if text_as == "text":
            is_text_as_path = False
        elif text_as == "fonts":
            is_text_as_path = False
        elif text_as == "paths":
            is_text_as_path = True
            
        svg = doc[page].get_svg_image(text_as_path=is_text_as_path)
        dst.write_text(svg, encoding="utf-8")
    except RuntimeError:
        raise
    except Exception as e:
        raise RuntimeError(f"[pymupdf] pdf_to_svg failed: {e}") from e
    finally:
        doc.close()
    return dst"""

content = re.sub(pdf_svg_regex, pdf_svg_new, content, flags=re.DOTALL)

svg_norm_regex = r"def svg_normalize\(src: Path, dst: Path, \*, page: int = 0, text_as_path: bool = True\) -> Path:.*?return dst"
svg_norm_new = """def svg_normalize(src: Path, dst: Path, *, page: int = 0, text_as: str | None = None) -> Path:
    \"\"\"Normalize SVG via pymupdf round-trip: open SVG, re-emit as SVG.\"\"\"
    _ensure_parent(dst)
    doc = _open(src, "svg_normalize")
    try:
        is_text_as_path = True
        if text_as == "text":
            is_text_as_path = False
        elif text_as == "fonts":
            is_text_as_path = False
        elif text_as == "paths":
            is_text_as_path = True
            
        svg = doc[page].get_svg_image(text_as_path=is_text_as_path)
        dst.write_text(svg, encoding="utf-8")
    except RuntimeError:
        raise
    except Exception as e:
        raise RuntimeError(f"[pymupdf] svg_normalize failed: {e}") from e
    finally:
        doc.close()
    return dst"""

content = re.sub(svg_norm_regex, svg_norm_new, content, flags=re.DOTALL)

with open('src/vexy_pdfsvgpy/backends/pymupdf_backend.py', 'w') as f:
    f.write(content)
