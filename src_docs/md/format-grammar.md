# Format grammar

File extensions cover the common case: `report.pdf` is a PDF and `report.png` is a PNG. When you need to say more, such as "a folder of PDFs" or "a layered SVG", you pass a format spec through `vinput`/`voutput` or `binput`/`boutput`.

## Syntax

A format spec is a format name, optionally followed by an underscore and one or two qualifier letters:

```text
{format}[_{packaging}[{content}]]
```

- `format` is `pdf`, `svg`, `png` or `jpg`.
- `packaging` is one letter: `d`, `m`, `l` or `s`.
- `content` is one letter: `o`, `t` or `b`. Only vector formats (`pdf`, `svg`) take it.

Letters are case-insensitive. A qualifier can be omitted when it equals the default.

| Qualifier | Code | Meaning |
|---|---|---|
| Packaging | `d` (default) | Collection of single files: one output per input. |
| Packaging | `m` | Multi-page file. |
| Packaging | `l` | Layered single-page file. |
| Packaging | `s` | Single-page file. |
| Content (vector only) | `o` (default) | Outlines: text as paths. |
| Content (vector only) | `t` | Text with embedded fonts. |
| Content (vector only) | `b` | Bitmap only. |

## Validation rules

`FormatSpec.parse()` rejects these combinations with `InvalidInput`:

- An unknown format, packaging or content letter.
- A content letter on `png` or `jpg`: `png_lo` fails.
- `svg_m`: SVG has no multi-page form.
- `jpg_l`: JPG has no layered form.
- More than two qualifier letters: `pdf_mot` fails.
- An empty spec or an empty qualifier such as `pdf_`.

`png_m` and `jpg_m` are accepted by the parser.

## Defaults and canonical form

When the content letter is omitted on a vector format, it becomes `o`. `str(spec)` returns the shortest form that parses back to the same spec:

```python
from vexy_pdfsvgpy import FormatSpec

FormatSpec.parse("pdf_do").__str__()   # 'pdf'
str(FormatSpec.parse("pdf_m"))         # 'pdf_mo'
str(FormatSpec.parse("png_l"))         # 'png_l'
str(FormatSpec.parse("svg_lt"))        # 'svg_lt'
```

`FormatSpec.from_extension(path)` maps `.pdf`, `.svg`, `.png`, `.jpg` and `.jpeg` to the default spec for that format. Any other extension raises `InvalidInput`.

## What the qualifiers change today

In the current release, `convert()` uses the spec like this:

- **Format** chooses the conversion. The planner looks only at the input and output format names. See [Architecture](architecture.md).
- **Input packaging `d`** allows a directory input. `convert()` collects every file with the matching extension and converts each one. Any other input packaging rejects a directory with `InvalidInput`.
- **Output packaging `d`** treats an output path that is an existing directory, or has no extension, as a directory. `convert()` creates it and writes `<stem>.<format>` inside.
- **Several inputs with output packaging `m` or `l`** raise `NotImplementedError`. Combining many files into one multi-page or layered document is not wired into `convert()` yet. The reshape functions `docs2pages_pdf`, `docs2layers_pdf` and `docs2layers_svg` in `vexy_pdfsvgpy.operations.reshape` do this directly; see [Python API](api.md#reshape-operations).
- **Content** is parsed and stored but does not select a backend or option. To outline text in PDF to SVG, use `text_as="paths"`.

## Example: a folder of PDFs

```python
from vexy_pdfsvgpy import convert

# Rasterize page 1 of every PDF in ./pdfs/ into ./pngs/<stem>.png
convert(input="./pdfs/", output="./pngs/", binput="pdf_d", boutput="png_d")
```

Step by step, for a folder containing `a.pdf` and `b.pdf`:

1. `binput="pdf_d"` parses to format `pdf`, packaging `d`, content `o`.
2. Because the input is a directory and the packaging is `d`, `convert()` collects `a.pdf` and `b.pdf`.
3. `boutput="png_d"` parses to format `png`, packaging `d`.
4. The planner picks the `pdf_to_png` capability for each file.
5. `convert()` creates `./pngs/` and writes `./pngs/a.png` and `./pngs/b.png`.
6. The call returns `[Path('pngs/a.png'), Path('pngs/b.png')]`.

## Flag precedence

`vinput` wins over `binput`, and `voutput` wins over `boutput`. Both pairs accept any format spec; the `v`/`b` prefix does not restrict the format.
