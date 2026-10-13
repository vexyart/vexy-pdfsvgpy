# Quick start

This page follows one PDF through the main operations. Each step shows the CLI command first and the Python call second.

## Before you start

- `vexy-pdfsvgpy` is installed. See [Installation](installation.md).
- You have a PDF file. The examples use `report.pdf`.

## Rasterize a PDF page to PNG

1. Run the conversion:

    ```bash
    vexy-pdfsvgpy convert --input report.pdf --output report.png
    ```

2. Read the summary table. It lists the input path, the output path and the output size in bytes.

The default backend, `pymupdf`, renders the first page (`page=0`) at 300 dpi. The same call from Python:

```python
from vexy_pdfsvgpy import convert

out = convert(input="report.pdf", output="report.png")
print(out)  # report.png
```

`convert()` returns the output path as a `pathlib.Path`.

To render at another resolution, pass the backend keyword through `convert()`:

```python
convert(input="report.pdf", output="report-72dpi.png", dpi=72)
```

Extra keyword arguments go straight to the backend function. The `pymupdf` PDF renderer accepts `page`, `dpi` and `alpha`. See [Python API](api.md#backend-keyword-arguments).

## Convert a PDF page to SVG

```bash
vexy-pdfsvgpy convert --input report.pdf --output report.svg
```

By default the SVG keeps text as `<text>` elements. To turn every glyph into an outline, add `--text_as paths`:

```bash
vexy-pdfsvgpy convert --input report.pdf --output report-outlined.svg --text_as paths
```

The outlined SVG renders the same without the fonts, but the text can no longer be selected or edited.

## Convert an SVG to PDF and PNG

```bash
vexy-pdfsvgpy convert --input logo.svg --output logo.pdf
vexy-pdfsvgpy convert --input logo.svg --output logo.png
```

SVG to PNG uses `resvg-py` by default and renders at 2048 pixels wide. To use `pymupdf` instead, which renders at 300 dpi, add `--hint mu`:

```bash
vexy-pdfsvgpy convert --input logo.svg --output logo.png --hint mu
```

## Trace a bitmap to SVG

```bash
vexy-pdfsvgpy convert --input scan.png --output scan.svg
```

`vtracer` traces the bitmap into color spline paths. JPG input works the same way.

## Wrap a bitmap in a PDF

```bash
vexy-pdfsvgpy convert --input scan.png --output scan.pdf
```

The bitmap is placed in a one-page PDF without tracing.

## Split and merge PDFs

1. Split a multi-page PDF into one file per page:

    ```bash
    vexy-pdfsvgpy split --input book.pdf --out_dir ./pages/
    ```

    For a three-page `book.pdf`, the result is `pages/book-pikepdf-page-01.pdf`, `pages/book-pikepdf-page-02.pdf` and `pages/book-pikepdf-page-03.pdf`.

2. Merge PDFs back into one file:

    ```bash
    vexy-pdfsvgpy merge --inputs "pages/book-pikepdf-page-01.pdf,pages/book-pikepdf-page-03.pdf" --output short.pdf
    ```

    The pages appear in the order of the comma-separated list.

## Normalize a PDF

```bash
vexy-pdfsvgpy regularize --input messy.pdf --output clean.pdf
```

`pymupdf` re-saves the file with cleaned content streams, deflate compression and unused objects removed (`garbage=4`).

## Convert a whole folder

A directory input needs an explicit format spec that says which files to pick up. The `d` packaging code means "a collection of single files":

```python
from vexy_pdfsvgpy import convert

paths = convert(input="./pdfs/", output="./pngs/", binput="pdf_d", boutput="png_d")
```

The call converts every `*.pdf` in `./pdfs/` (not recursively) and writes `./pngs/<stem>.png` for each. It returns a list of output paths when more than one file matched. See [Format grammar](format-grammar.md).

## Next steps

- [CLI reference](cli.md) lists every flag.
- [Backends](backends.md) explains hints.
- [Troubleshooting](troubleshooting.md) lists current limitations.
