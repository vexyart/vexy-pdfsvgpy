# vexy-pdfsvgpy

`vexy-pdfsvgpy` is a Python library and command-line tool that converts files between PDF, SVG, PNG and JPG. You call one function, `convert()`, or one command, `vexy-pdfsvgpy convert`. The extension of the output file decides the target format.

Every backend installs as a normal pip wheel. The package does not need Cairo, Poppler, Ghostscript or any other system library.

![One convert() call, no system libraries](assets/icon.png){ width="280" }

## What it does

| Input | Output | Default backend |
|---|---|---|
| PDF | PNG | `pymupdf` |
| PDF | SVG | `pymupdf` |
| SVG | PNG | `resvg-py` |
| SVG | PDF | `pymupdf` |
| PNG or JPG | SVG (traced) | `vtracer` |
| PNG or JPG | PDF (wrapped) | `pymupdf` |
| PDF | PDF (normalized) | `pymupdf` |
| SVG | SVG (normalized) | `pymupdf` |

The CLI also splits a multi-page PDF into one file per page and merges several PDFs into one.

## One call

```python
from vexy_pdfsvgpy import convert

convert(input="report.pdf", output="report.png")   # rasterize page 1
convert(input="logo.svg", output="logo.pdf")        # SVG to PDF
convert(input="report.pdf", output="report.svg")    # PDF page 1 to SVG
```

## From the shell

```bash
vexy-pdfsvgpy convert --input report.pdf --output report.png
vexy-pdfsvgpy split --input report.pdf --out_dir ./pages/
vexy-pdfsvgpy merge --inputs "a.pdf,b.pdf" --output book.pdf
```

## Why it exists

Many PDF and SVG toolchains fail once they leave the machine they were built on: `libcairo` is missing, the Poppler version differs, or a Homebrew formula has changed. `vexy-pdfsvgpy` follows one rule: after `pip install`, it works. Each backend was chosen because it ships as a self-contained wheel.

The cost is fidelity in some directions. PDF to SVG is lossy: groups are flattened, and with `text_as="paths"` the text becomes outlines that can no longer be selected. See [Backends](backends.md).

## Where to go next

- [Installation](installation.md): requirements and optional extras.
- [Quick start](quickstart.md): your first conversions, step by step.
- [CLI reference](cli.md): every subcommand and flag.
- [Python API](api.md): `convert()`, `FormatSpec`, `Hints`, `plan()`, `execute()` and the error classes.
- [Format grammar](format-grammar.md): format specs such as `pdf_mo` and `svg_lt`.
- [Backends](backends.md): which library handles each conversion, and how to choose another one.
- [Architecture](architecture.md): how a call moves through the planner and dispatcher.
- [Troubleshooting](troubleshooting.md): known limitations and common errors.
- [Contributing](contributing.md): development setup, tests and releases.
