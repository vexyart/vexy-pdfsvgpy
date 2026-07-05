---
this_file: docs/backends.md
title: Backends
layout: default
nav_order: 2
---

# Backends

Every conversion is handled by one deterministic backend, chosen by capability rather than by user flag. When a real fidelity or speed tradeoff exists, a second backend is offered and you can force it with a `hints` string.

| Capability | Primary | Alternate | Hint codes |
|---|---|---|---|
| PDF → PNG | `pymupdf` | `pypdfium2`, Quartz | `mu` / `ap` |
| PDF → SVG | `pymupdf` | — | `mu` |
| SVG → PNG | `resvg-py` | `pymupdf` | `re` / `mu` |
| SVG → PDF | `pymupdf` | — | `mu` |
| PNG/JPG → SVG (trace) | `vtracer` | — | — |
| PNG/JPG → PDF (wrap) | `pymupdf` | `pikepdf` | — |
| PDF split | `pypdf` | `pikepdf`, Quartz | `pk` / `ap` |
| PDF merge | `pikepdf` | `pypdf`, Quartz | `pk` / `ap` |
| PDF normalize | `pymupdf` | Quartz | `mu` / `ap` |
| PDF/SVG layers | `pymupdf` / `lxml` | `pikepdf` | `mu` / `pk` |

## Forcing a backend

```python
from vexy_pdfsvgpy import convert

# Force resvg for SVG → PNG instead of the default pick.
convert(input="logo.svg", output="logo.png", hints="re")
```

Hint codes: `mu` (pymupdf), `ap` (Apple Quartz, macOS only), `re` (resvg), `pk` (pikepdf).

## Lossy paths

PDF → SVG is inherently lossy. `pymupdf` flattens glyphs to vector outlines: the shapes are faithful, but text is no longer selectable and groups are gone. The API never pretends otherwise — treat it as "make this PDF drawable as SVG", not "round-trip this document".

## Rejected backends

`cairosvg`, `pdf2image`, `svglib`, `reportlab`, `skia-python`, `pdfkit`, `weasyprint`, and anything needing Cairo, Poppler, or Ghostscript are excluded on purpose. The rule is non-negotiable: a backend must install as a self-contained wheel with no post-install step. `SPEC.md` records the full rationale.

## Optional extras

Two backends stay behind extras because they pull system tooling and only earn their place in niche cases:

```bash
pip install "vexy-pdfsvgpy[cairo]"        # CairoSVG
pip install "vexy-pdfsvgpy[ghostscript]"  # Ghostscript
pip install "vexy-pdfsvgpy[all]"          # both
```
