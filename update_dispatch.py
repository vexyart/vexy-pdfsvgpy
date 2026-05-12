import re

with open('src/vexy_pdfsvgpy/dispatch.py', 'r') as f:
    content = f.read()

dispatch_regex = r"return \{c: tuple\(v\) for c, v in table\.items\(\)\}"
dispatch_new = """# cairo - optional backend for CA hint
    try:
        from .backends import cairo_backend as c
        table[Capability.SVG_TO_PNG].append(BackendFn("cairo", Hint.CA, c.svg_to_png))
        table[Capability.SVG_TO_PDF].append(BackendFn("cairo", Hint.CA, c.svg_to_pdf))
    except ImportError:
        pass

    # ghostscript - optional backend for GS hint
    try:
        from .backends import ghostscript_backend as gs
        table[Capability.PDF_TO_PNG].append(BackendFn("ghostscript", Hint.GS, gs.pdf_to_png))
        table[Capability.PDF_NORMALIZE].append(BackendFn("ghostscript", Hint.GS, gs.pdf_normalize))
    except ImportError:
        pass

    return {c: tuple(v) for c, v in table.items()}"""

content = re.sub(dispatch_regex, dispatch_new, content)

with open('src/vexy_pdfsvgpy/dispatch.py', 'w') as f:
    f.write(content)
