---
this_file: docs/index.md
title: Home
layout: default
nav_order: 1
---

# vexy-pdfsvgpy

One `convert()` call moves a file across the PDF ⇄ SVG ⇄ PNG/JPG graph. No Poppler, no Cairo, no Ghostscript, no system libraries — every backend ships as a plain pip wheel.

![icon](assets/icon.png){: style="max-width:280px"}

## Install

```bash
pip install vexy-pdfsvgpy   # or: uv add vexy-pdfsvgpy
```

Python 3.12+.

## One call

```python
from vexy_pdfsvgpy import convert

convert(input="report.pdf", output="report.png")   # rasterize
convert(input="logo.svg",  output="logo.pdf")       # vectorize
convert(input="report.pdf", output="report.svg")    # extract (lossy — text becomes paths)
```

The output extension decides the target format. That is the entire mental model.

## From the shell

```bash
vexy-pdfsvgpy convert --input report.pdf --output report.png
vexy-pdfsvgpy split   --input report.pdf --out_dir ./pages/
vexy-pdfsvgpy merge   --inputs "a.pdf,b.pdf" --output book.pdf
```

## Where to go next

- [Backends](backends.md) — which library does each conversion, and how to force one.
- [Format grammar](format-grammar.md) — the `{format}-{packaging}{content}` spec strings.
- [CLI reference](cli.md) — every subcommand and flag.

## Why it exists

Most PDF/SVG toolchains break the moment they leave your laptop: a missing `libcairo`, a Poppler version mismatch, a Homebrew formula that vanished. vexy-pdfsvgpy takes one rule seriously — **pip install, then it works, everywhere** — and picks its backends to honor it. The tradeoff is deliberate: PDF → SVG flattens text to paths. You get portability, not semantic fidelity, and the API says so out loud.
