---
this_file: docs/format-grammar.md
title: Format grammar
layout: default
nav_order: 3
---

# Format grammar

Extensions cover the common case. When you need to say more — "a multi-page PDF with real text" or "a layered SVG" — use an explicit format spec via `vinput`/`voutput` (or `binput`/`boutput` for bitmap sides).

A spec is `{format}-{packaging}{content}`. Either qualifier can be dropped when it equals the default.

| Qualifier | Codes | Meaning |
|---|---|---|
| Packaging (vector) | `d` (default), `m`, `l`, `s` | collection / multi-page / layered / single-page |
| Packaging (bitmap) | `d` (default), `l` | collection / layered (APNG) |
| Content (vector) | `o` (default), `t`, `b` | outlines / text / bitmap-only |

Examples:

- `pdf_mo` — multi-page PDF, outline text.
- `svg_lt` — layered SVG, text preserved.
- `png` — same as `png_d`.

```python
from vexy_pdfsvgpy import convert

# Treat a directory of PDFs as a collection and rasterize each.
convert(input="./pdfs/", output="./pngs/", binput="pdf_d", boutput="png_d")
```

```python
from vexy_pdfsvgpy import FormatSpec

spec = FormatSpec.parse("svg_lt")
assert str(spec) == "svg_lt"   # round-trips
```

## Multi-file inputs

`packaging=d` (collection) processes each file independently and writes one output per input. Combining several inputs into a single multi-page or layered document (`m` / `l`) is specified in the grammar but not yet wired end to end — see [TODO.md](https://github.com/vexyart/vexy-pdfsvgpy/blob/main/TODO.md).
