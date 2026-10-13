# CLI reference

The `vexy-pdfsvgpy` command is a [Fire](https://github.com/google/python-fire) wrapper around the same functions the Python API uses. It is installed as a console script and can also run as `python -m vexy_pdfsvgpy`.

```bash
vexy-pdfsvgpy SUBCOMMAND [--flag VALUE ...]
```

Fire maps each keyword argument to a `--flag`. Boolean flags are switched on by naming them, for example `--recursive`. Run `vexy-pdfsvgpy SUBCOMMAND --help` to see the signature of one subcommand.

## Exit codes

| Code | Meaning |
|---|---|
| `0` | Success. |
| `1` | The conversion failed. The CLI prints the error class and message, for example `UnsupportedConversion: identity conversion png → png is not supported`. |
| `2` | `convert` was called without `--input` or `--output`. |

Fire also prints the integer return value (`0`, `1` or `2`) on its own line.

## convert

```bash
vexy-pdfsvgpy convert --input IN --output OUT [flags]
```

Converts one file, or a directory of files, to another format. The input and output formats come from the file extensions (`.pdf`, `.svg`, `.png`, `.jpg`, `.jpeg`) unless you set them with a format spec.

### Format and backend flags

| Flag | Value | Effect |
|---|---|---|
| `--input` | path | Source file or directory. Required. |
| `--output` | path | Destination file or directory. Required. |
| `--vinput` | format spec | Input format, for example `pdf_d`. Overrides the extension. |
| `--voutput` | format spec | Output format, for example `svg_lt`. Overrides the extension. |
| `--binput` | format spec | Input format. Used only when `--vinput` is not given. |
| `--boutput` | format spec | Output format. Used only when `--voutput` is not given. |
| `--hint` | hint codes | Preferred backend, for example `re` or `mu,ap`. See [Backends](backends.md#hints). |
| `--recursive` | switch | With a directory input, search subdirectories too. |
| `--glob` | pattern | With a directory input, select files with this glob pattern, for example `"*/*.pdf"`. Files must still match the input format's extension. |
| `--text_as` | `paths` | PDF to SVG or SVG normalization: convert text to outlines. Any other value, or no flag, keeps text as `<text>` elements. |
| `--verbose` | switch | Set the log level to `DEBUG`. The CLI currently discards log messages, so this adds no output. |

The `v` and `b` flags take the same format specs. The CLI checks `--vinput` before `--binput` and `--voutput` before `--boutput`. See [Format grammar](format-grammar.md).

### Transform flags

`convert` also accepts these flags:

`--regularize`, `--dim`, `--scale`, `--top`, `--bottom`, `--left`, `--right`, `--crop`, `--gray`, `--invert`, `--vivid`, `--bright`, `--contrast`, `--backdrop`.

!!! warning "Transform flags are not wired up yet"
    In the current release these flags are passed unchanged to the backend function. No backend accepts them, so a conversion that uses one fails with exit code `1`, for example:

    ```text
    BackendFailure:  pdf_to_png failed: pdf_to_png() got an unexpected keyword argument 'gray'
    ```

    The exception is a same-format conversion such as PDF to PDF, where the CLI ignores extra options. The `regularize` subcommand relies on this. The size, crop and color operations exist as library modules (`vexy_pdfsvgpy.operations.sizecrop` and `vexy_pdfsvgpy.operations.color`) but are not yet called by `convert`.

### Directory input

When `--input` is a directory:

1. Set the input format with `--vinput` or `--binput`. Without it, the call fails with `Must specify explicit format specifier (e.g. --binput png_d) for directories`.
2. Use packaging `d` for the input format, for example `pdf_d`. Other packaging codes reject a directory.
3. The command collects files with the matching extension (in both cases, for example `*.pdf` and `*.PDF`) from the directory, from its subdirectories with `--recursive`, or by `--glob`.
4. With an output packaging of `d`, the command creates the output directory and writes one `<stem>.<format>` file per input.

The summary table shows the last file written.

### Examples

```bash
# Extension-driven
vexy-pdfsvgpy convert --input report.pdf --output report.png

# PDF to SVG with outlined text
vexy-pdfsvgpy convert --input report.pdf --output report.svg --text_as paths

# Prefer Apple Quartz for PDF to PNG (macOS only)
vexy-pdfsvgpy convert --input report.pdf --output report.png --hint ap

# Every PDF under ./pdfs, including subfolders, to ./pngs/<stem>.png
vexy-pdfsvgpy convert --input pdfs --output pngs --vinput pdf_d --boutput png_d --recursive
```

## regularize

```bash
vexy-pdfsvgpy regularize --input IN --output OUT [--hint CODES] [--verbose]
```

Runs `convert` with `regularize=True`. Use the same format on both sides:

- PDF to PDF uses the `pdf_normalize` capability: `pymupdf` re-saves the document with `clean=True`, `deflate=True` and `garbage=4`. `--hint ap` uses Apple PDFKit on macOS instead.
- SVG to SVG uses `svg_normalize`: `pymupdf` opens the SVG and writes the first page back out as SVG.

```bash
vexy-pdfsvgpy regularize --input messy.pdf --output clean.pdf
```

## split

```bash
vexy-pdfsvgpy split --input IN.pdf [--out_dir DIR] [--verbose]
```

Writes one PDF per page with `pikepdf`, without re-encoding the pages. Without `--out_dir`, the files go next to the input. File names follow `{stem}-pikepdf-page-{NN}.pdf`; the page number has at least two digits.

```bash
vexy-pdfsvgpy split --input book.pdf --out_dir ./pages/
# Split book.pdf into 3 page(s) in pages
```

## merge

```bash
vexy-pdfsvgpy merge --inputs "A.pdf,B.pdf,..." [--output OUT.pdf] [--verbose]
```

Concatenates PDFs with `pikepdf`, in the order given. `--inputs` is one comma-separated string. Without `--output`, the result is `<first-stem>-merged.pdf` next to the first input.

```bash
vexy-pdfsvgpy merge --inputs "a.pdf,b.pdf,c.pdf" --output book.pdf
# Merged 3 file(s) into book.pdf
```

## version

```bash
vexy-pdfsvgpy version
```

Prints the package version.

## Format shortcuts

Every valid format spec that contains an underscore is also a subcommand. The shortcut runs `convert` with `--voutput` set to that spec and accepts all other `convert` flags:

```bash
# Same as: vexy-pdfsvgpy convert --input a.pdf --output a.svg --voutput svg_s
vexy-pdfsvgpy svg_s --input a.pdf --output a.svg
```

Bare names such as `pdf` or `svg` are not registered. The CLI registers these 35 shortcuts:

| Format | Shortcuts |
|---|---|
| PDF | `pdf_d`, `pdf_db`, `pdf_do`, `pdf_dt`, `pdf_l`, `pdf_lb`, `pdf_lo`, `pdf_lt`, `pdf_m`, `pdf_mb`, `pdf_mo`, `pdf_mt`, `pdf_s`, `pdf_sb`, `pdf_so`, `pdf_st` |
| SVG | `svg_d`, `svg_db`, `svg_do`, `svg_dt`, `svg_l`, `svg_lb`, `svg_lo`, `svg_lt`, `svg_s`, `svg_sb`, `svg_so`, `svg_st` |
| PNG | `png_d`, `png_l`, `png_m`, `png_s` |
| JPG | `jpg_d`, `jpg_m`, `jpg_s` |

The top-level `vexy-pdfsvgpy --help` does not list subcommands, because Fire shows only the class description. Use `vexy-pdfsvgpy convert --help` to see the flags of `convert`.
