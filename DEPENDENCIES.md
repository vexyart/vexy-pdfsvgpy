---
this_file: DEPENDENCIES.md
---

# Dependencies

## Runtime

| Package | Why | Alternative rejected |
|---|---|---|
| `pymupdf` | PDF ⇄ SVG, PDF → PNG, normalize; the most versatile backend | PyMuPDF alternatives need Poppler/Cairo |
| `pypdfium2` | Alternate PDF → PNG, different speed/fidelity | `pdf2image` needs Poppler |
| `pypdf` | Pure-Python PDF split/merge, zero deps | `PyPDF2` is EOL |
| `pikepdf` | Lossless PDF split/merge, Form-XObject overlay | `PyPDF3` lacks FX support |
| `resvg-py` | SVG → PNG via Rust usvg/resvg, high fidelity | `cairosvg` needs Cairo |
| `vtracer` | Only pure-pip PNG/JPG → SVG tracer | `potrace` needs binary |
| `Pillow` | Bitmap metadata, color ops, test fixtures | — |
| `lxml` | Layered SVG `<g>` splitting/composition | stdlib `xml.etree` doesn't preserve namespaces cleanly |
| `fire` | Zero-boilerplate CLI from a class | `click` requires decorators |
| `loguru` | Debug logging with one-call setup | stdlib `logging` needs ceremony |
| `rich` | CLI tables and colored output | raw print lacks structure |
| `pyobjc-framework-Quartz` (darwin) | macOS `ap` hint: PDFKit + CoreGraphics native path | — |
| `pyobjc-framework-Cocoa` (darwin) | Required by Quartz wrappers | — |

## Dev

| Package | Why |
|---|---|
| `pytest` | test runner |
| `pytest-cov` | coverage reports |
| `mypy` | static type checks |
| `ruff` | lint and format |

## Forbidden / rejected

See `SPEC.md` §2. Explicit reject list: `cairosvg`, `pdf2image`, `svglib`, `reportlab` (as PDF renderer), `skia-python`, `pdfkit`, `weasyprint`, anything needing Cairo / Poppler / Ghostscript / libcairo.
