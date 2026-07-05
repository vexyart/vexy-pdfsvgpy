---
this_file: docs/cli.md
title: CLI reference
layout: default
nav_order: 4
---

# CLI reference

The CLI is a thin Fire wrapper over the same functions the Python API calls. Every subcommand returns a shell exit code: `0` success, `1` a conversion error, `2` bad arguments.

## convert

```bash
vexy-pdfsvgpy convert --input IN --output OUT [flags]
```

Format is inferred from extensions, or set explicitly:

| Flag | Purpose |
|---|---|
| `--vinput` / `--voutput` | vector-side format spec (e.g. `svg_lt`) |
| `--binput` / `--boutput` | bitmap-side format spec (e.g. `png_d`) |
| `--hint` | force a backend (`mu`, `ap`, `re`, `pk`) |
| `--recursive` / `--glob` | expand a directory input |

Transform flags (applied during conversion):

| Flag | Effect |
|---|---|
| `--regularize` | canonicalize the document |
| `--text_as` | `path` or `text` for PDF → SVG glyph handling |
| `--dim` / `--scale` / `--crop` | resize and crop |
| `--top` `--bottom` `--left` `--right` | margins |
| `--gray` `--invert` `--vivid` `--bright` `--contrast` `--backdrop` | color operations |
| `--verbose` | debug logging |

## split

```bash
vexy-pdfsvgpy split --input book.pdf --out_dir ./pages/
```

Writes one PDF per page.

## merge

```bash
vexy-pdfsvgpy merge --inputs "a.pdf,b.pdf,c.pdf" --output book.pdf
```

Comma-separated inputs, concatenated into one PDF.

## regularize

```bash
vexy-pdfsvgpy regularize --input messy.pdf --output clean.pdf
```

Shortcut for `convert --regularize`.

## Format shortcuts

Every valid format spec is also a subcommand: `vexy-pdfsvgpy svg_lt --input a.pdf --output a.svg` is `convert --voutput svg_lt`. Run `vexy-pdfsvgpy --help` to list them.
