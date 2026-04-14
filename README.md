---
this_file: README.md
---

# vexy-pdfsvgpy

Unified Python API and CLI for PDF ⇄ SVG ⇄ PNG/JPG conversion — pure-pip, no Cairo, no Poppler, no system libraries.

## Install

```bash
uv add vexy-pdfsvgpy
# or
pip install vexy-pdfsvgpy
```

Python 3.12+ required.

## Quick start

**Python API:**

```python
from vexy_pdfsvgpy import convert

# PDF → PNG
convert(input="document.pdf", output="document.png")

# SVG → PDF
convert(input="logo.svg", output="logo.pdf")

# PDF → SVG (lossy — text converted to paths)
convert(input="document.pdf", output="document.svg")
```

**CLI:**

```bash
# Convert PDF to PNG
vexy-pdfsvgpy convert --input document.pdf --output document.png

# Split a multi-page PDF into per-page files
vexy-pdfsvgpy split --input document.pdf --out_dir ./pages/

# Merge PDFs
vexy-pdfsvgpy merge --inputs "a.pdf,b.pdf,c.pdf" --output merged.pdf

# Regularize (canonicalize) a PDF
vexy-pdfsvgpy regularize --input messy.pdf --output clean.pdf
```

## Format grammar

Format specs follow `{format}-{packaging}{content}`. Either qualifier can be omitted when equal to the default.

| Qualifier | Codes | Meaning |
|-----------|-------|---------|
| Packaging (vector) | `d` (default), `m`, `l`, `s` | collection / multi-page / layered / single-page |
| Packaging (bitmap) | `d` (default), `l` | collection / layered (APNG) |
| Content (vector) | `o` (default), `t`, `b` | outlines / text / bitmap-only |

Examples: `pdf-mo` = multi-page PDF with outline text. `svg-lt` = layered SVG with preserved text. `png` = `png-d`.

**Note:** PDF → SVG is inherently lossy. Text is converted to paths (`text_as_path=True`). Semantic fidelity is not guaranteed.

## Backends

| Capability | Primary | Alternate | Hint |
|---|---|---|---|
| PDF → PNG | `pymupdf` | `pypdfium2`, Quartz (`ap`) | `mu` / `ap` |
| PDF → SVG | `pymupdf` | — | `mu` |
| SVG → PNG | `resvg-py` | `pymupdf` | `re` / `mu` |
| SVG → PDF | `pymupdf` | — | `mu` |
| PNG/JPG → SVG (trace) | `vtracer` | — | — |
| PNG/JPG → PDF (wrap) | `pymupdf` | `pikepdf` | — |
| PDF split | `pypdf` | `pikepdf`, Quartz | `pk` / `ap` |
| PDF merge | `pikepdf` | `pypdf`, Quartz | `pk` / `ap` |
| PDF normalize | `pymupdf` | Quartz (`ap`) | `mu` / `ap` |
| SVG normalize | `pymupdf` round-trip | `resvg` raster-wrap | `mu` / `re` |
| PDF layers (OCGs) | `pymupdf` | `pikepdf` | `mu` / `pk` |
| SVG layers (`<g>`) | `lxml` | — | — |

Pass `hints` to prefer a specific backend: `convert(..., hints="re")` forces resvg for SVG → PNG.

## Rejected backends

`cairosvg`, `pdf2image`, `svglib`, `reportlab`, `skia-python`, `pdfkit`, `weasyprint`, and anything requiring Cairo, Poppler, or Ghostscript are explicitly excluded. The rule is strict: every backend must ship as a self-contained wheel with no post-install setup. See `SPEC.md` §2 for the full rationale and rejection notes.

## Examples

See `examples/` for runnable scripts:

- `convert_coupon.py` — split a PDF, rasterize pages at 300 dpi, re-merge
- `trace_logo.py` — SVG → PNG → traced SVG round-trip via vtracer
- `layer_stack.py` — stack SVGs into a layered PDF (OCGs) and layered SVG
- `regularize_batch.py` — canonicalize every fixture in `testdata/`

## License

See `LICENSE`.

## Links

- [SPEC.md](SPEC.md) — full specification
- [TODO.md](TODO.md) — task list
- [CHANGELOG.md](CHANGELOG.md) — release history
- [DEPENDENCIES.md](DEPENDENCIES.md) — dependency rationale
