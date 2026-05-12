import re

with open('src/vexy_pdfsvgpy/types.py', 'r') as f:
    content = f.read()

# Add new hint constants
hint_regex = r"class Hint\(StrEnum\):\n    RE = \"re\"  # prefer resvg\n    MU = \"mu\"  # prefer pymupdf\n    PK = \"pk\"  # prefer pikepdf\n    AP = \"ap\"  # prefer Apple PDFKit / Quartz \(macOS only\)"
hint_new = """class Hint(StrEnum):
    RE = "re"  # prefer resvg
    MU = "mu"  # prefer pymupdf
    PK = "pk"  # prefer pikepdf
    AP = "ap"  # prefer Apple PDFKit / Quartz (macOS only)
    CA = "ca"  # prefer Cairo
    GS = "gs"  # prefer Ghostscript"""

content = re.sub(hint_regex, hint_new, content)

with open('src/vexy_pdfsvgpy/types.py', 'w') as f:
    f.write(content)
