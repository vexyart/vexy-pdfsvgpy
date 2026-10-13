# Backends

Each conversion is one *capability*, such as `pdf_to_png`. Each capability has an ordered list of backend functions. Without hints, the first backend in the list runs. A hint moves another backend to the front when a real speed or fidelity trade-off exists.

## Capability table

This is the table the dispatcher builds on import. The left-most backend is the default.

| Capability | Backends, in order (hint code) | Default output |
|---|---|---|
| `pdf_to_png` | `pymupdf` (`mu`), `pdfium` (`mu`), `apple` (`ap`), `ghostscript` (`gs`) | Page 1 at 300 dpi |
| `pdf_to_svg` | `pymupdf` (`mu`) | Page 1, text kept as `<text>` |
| `svg_to_png` | `resvg` (`re`), `pymupdf` (`mu`), `cairo` (`ca`) | 2048 px wide |
| `svg_to_pdf` | `pymupdf` (`mu`), `cairo` (`ca`) | One-page PDF |
| `png_to_svg_trace` | `vtracer` (`re`) | Color spline tracing; used for PNG and JPG input |
| `bitmap_to_pdf` | `wrap` (`mu`) | Bitmap placed in a PDF page by `pymupdf` |
| `pdf_normalize` | `pymupdf` (`mu`), `apple` (`ap`), `ghostscript` (`gs`) | `clean=True`, `deflate=True`, `garbage=4` |
| `svg_normalize` | `pymupdf` (`mu`) | First page re-emitted as SVG |
| `pdf_split` | `pypdf` (`pk`), `pikepdf` (`pk`), `apple` (`ap`) | Not used by `convert()` |
| `pdf_merge` | `pikepdf` (`pk`), `pypdf` (`pk`), `apple` (`ap`) | Not used by `convert()` |
| `png_to_svg_wrap` | `wrap` (`mu`) | Not used by `convert()` |

The `split` and `merge` CLI subcommands call `pikepdf` directly through `vexy_pdfsvgpy.operations.reshape`, not through the dispatcher.

`pdfium` shares the `mu` hint with `pymupdf`, which comes first, so a hint cannot select `pdfium`. Call `vexy_pdfsvgpy.backends.pdfium_backend.pdf_to_png()` directly to use it.

## Hints

A hint is a two-letter code. You can pass several, separated by commas; the order sets the priority.

| Code | Backend |
|---|---|
| `mu` | PyMuPDF |
| `re` | resvg (and `vtracer`, which is registered under `re`) |
| `pk` | pypdf / pikepdf |
| `ap` | Apple PDFKit and Quartz (macOS only) |
| `ca` | CairoSVG (needs the `cairo` extra) |
| `gs` | Ghostscript (needs the `ghostscript` extra) |

The dispatcher goes through your hints in order. For the first hint that matches a backend of the capability, that backend runs. If no hint matches, the default runs. An unknown code raises `InvalidInput`.

```python
from vexy_pdfsvgpy import convert

# SVG to PNG with pymupdf instead of resvg
convert(input="logo.svg", output="logo.png", hints="mu")

# Try Apple first, then pymupdf
convert(input="report.pdf", output="report.png", hints="ap,mu")
```

From the shell, use `--hint`:

```bash
vexy-pdfsvgpy convert --input logo.svg --output logo.png --hint mu
```

## Backend details

### PyMuPDF (`pymupdf`)

The default for most capabilities.

- `pdf_to_png(src, dst, *, page=0, dpi=300, alpha=False)`
- `pdf_to_svg(src, dst, *, page=0, text_as=None)`. With `text_as="paths"` the SVG contains outlines; any other value keeps `<text>` elements that reference the PDF fonts.
- `svg_to_png(src, dst, *, dpi=300, alpha=True)`
- `svg_to_pdf(src, dst)`
- `pdf_normalize(src, dst)`
- `svg_normalize(src, dst, *, page=0, text_as=None)`

### resvg (`resvg-py`)

The default SVG rasterizer.

- `svg_to_png(src, dst, *, width=2048)` renders at the given pixel width.

Some SVGs set `width` and `height` in `pt`, which `resvg` rejects with an "invalid size" error. The backend then rewrites those attributes as plain numbers and renders again once.

### pypdfium2 (`pdfium`)

- `pdf_to_png(src, dst, *, page=0, dpi=300)` renders with `scale=dpi/72` and saves through Pillow.

### vtracer

- `trace(src, dst, *, colormode="color", mode="spline", filter_speckle=4, color_precision=6, layer_difference=16, corner_threshold=60, length_threshold=4.0, max_iterations=10, splice_threshold=45, path_precision=8)`

`colormode` is `"color"` or `"binary"`. `mode` is `"spline"`, `"polygon"` or `"pixel"`. Pass any of these as keyword arguments to `convert()` when the input is PNG or JPG and the output is SVG:

```python
convert(input="logo.png", output="logo.svg", colormode="binary", mode="polygon")
```

### wrap

Places a bitmap in a vector container without tracing.

- `png_to_pdf(src, dst)` and `jpg_to_pdf(src, dst)` open the bitmap with `pymupdf` and save it as a PDF.
- `png_to_svg(src, dst)`, `jpg_to_svg(src, dst)` and `bitmap_to_svg(src, dst, *, mime=None)` embed the image as a base64 `<image>` in a minimal SVG with the bitmap's pixel size.

### pikepdf and pypdf

Lossless page operations. `split(src, out_dir, *, stem=None)` writes `{stem}-pikepdf-page-{NN}.pdf` (or `-pypdf-` for pypdf). `merge(srcs, dst)` concatenates the pages of each input in order. `pikepdf_backend.overlay_pages(base, overlays, dst)` also exists.

### Apple (`ap`)

Uses PDFKit and CoreGraphics through PyObjC. It is installed only on macOS. On other platforms the module imports, but each call raises an error that `convert()` reports as `BackendFailure`.

- `pdf_to_png(src, dst, *, page=0, width=2048)`
- `pdf_normalize(src, dst)`
- `split(src, out_dir, *, stem=None)` and `merge(srcs, dst)`

### Cairo (`ca`) and Ghostscript (`gs`)

Optional, behind the `cairo` and `ghostscript` extras. Both modules are always registered, but they import their library only when called. Without the extra, a `ca` or `gs` hint fails at conversion time.

- Cairo: `svg_to_png(src, dst, *, dpi=300)`, `svg_to_pdf(src, dst)`
- Ghostscript: `pdf_to_png(src, dst, *, page=0, dpi=300)`, `pdf_normalize(src, dst, *, text_as=None)`

## Lossy paths

PDF to SVG is lossy. PyMuPDF writes the drawing operations of one page as SVG: the shapes match, but groups and document structure are gone. With `text_as="paths"` the text also stops being text. Treat PDF to SVG as "make this page drawable as SVG", not as a round trip.

## Rejected backends

`cairosvg` as a default, `pdf2image`, `svglib`, `reportlab`, `skia-python`, `pdfkit`, `weasyprint`, and anything that needs Cairo, Poppler or Ghostscript at install time are excluded on purpose. A default backend must install as a self-contained wheel with no post-install step. CairoSVG and Ghostscript are reachable only through the opt-in extras. `SPEC.md` and `IDEA.md` in the repository record the full reasoning.
