# Python API

Everything on this page is importable from `vexy_pdfsvgpy` unless a module path is given.

```python
from vexy_pdfsvgpy import (
    convert, plan, execute, Step,
    FormatSpec, Packaging, Content, Hint, Hints,
    Capability, Document, Page,
    VexyError, InvalidInput, UnsupportedConversion, BackendFailure, UnsupportedOnPlatform,
    __version__,
)
```

## convert()

```python
convert(
    input: str | Path | None = None,
    output: str | Path | None = None,
    *,
    vinput: str | None = None,
    voutput: str | None = None,
    binput: str | None = None,
    boutput: str | None = None,
    hints: str | Hints | None = None,
    **options,
) -> Path | list[Path]
```

The single entry point. It takes an input path and an output path, works out the formats, plans the conversion and runs it.

| Parameter | Meaning |
|---|---|
| `input` | Source file or directory. Must exist. |
| `output` | Destination file, or a directory for packaging `d`. |
| `vinput`, `binput` | Input [format spec](format-grammar.md). `vinput` wins if both are set. Required when `input` is a directory. |
| `voutput`, `boutput` | Output format spec. `voutput` wins if both are set. |
| `hints` | Backend preference, as a string such as `"re,mu"` or a `Hints` object. See [Backends](backends.md#hints). |
| `recursive` | Option. With a directory input, search subdirectories. |
| `glob` | Option. With a directory input, select files with this glob pattern. |
| `**options` | Everything else is passed to the backend function. See below. |

Return value:

- One input file: the output `Path`.
- Several input files (directory input): a list of output paths.

What `convert()` does, in order:

1. Checks that `input` and `output` are given and that `input` exists. Otherwise it raises `InvalidInput`.
2. Builds the input spec from `vinput`, `binput`, or the input extension.
3. Builds the output spec from `voutput`, `boutput`, or the output extension.
4. Collects the input files. A directory is expanded only for input packaging `d`.
5. Calls `plan()` and `execute()` for each file.

### Backend keyword arguments

Options other than `recursive` and `glob` go to the backend function unchanged. Use them to set the page, resolution or tracing parameters:

```python
# Second page at 150 dpi with pymupdf
convert(input="report.pdf", output="page2.png", page=1, dpi=150)

# SVG at 1024 px wide with resvg
convert(input="logo.svg", output="logo.png", width=1024)

# PDF page to SVG with outlined text
convert(input="report.pdf", output="report.svg", text_as="paths")
```

The accepted names depend on which backend runs; see [Backend details](backends.md#backend-details). If the backend does not accept a keyword, the call raises `BackendFailure` with the `TypeError` message. For example, `dpi` works with `pymupdf` for SVG to PNG but not with `resvg`, which takes `width`.

Same-format conversions (PDF to PDF, SVG to SVG) ignore options.

## FormatSpec

```python
@dataclass(frozen=True, slots=True)
class FormatSpec:
    format: Literal["pdf", "svg", "png", "jpg"]
    packaging: Packaging = Packaging.D
    content: Content | None = None
```

| Member | Description |
|---|---|
| `FormatSpec.parse(s)` | Parse a string such as `"pdf_mo"`. Raises `InvalidInput`. |
| `FormatSpec.from_extension(path)` | Default spec for `.pdf`, `.svg`, `.png`, `.jpg`, `.jpeg`. |
| `str(spec)` | Shortest canonical form; round-trips with `parse()`. |
| `spec.is_vector` | `True` for `pdf` and `svg`. |
| `spec.is_bitmap` | `True` for `png` and `jpg`. |

```python
spec = FormatSpec.parse("svg_lt")
spec.format       # 'svg'
spec.packaging    # <Packaging.L: 'l'>
spec.content      # <Content.T: 't'>
str(spec)         # 'svg_lt'
```

`Packaging` has the members `D`, `M`, `L`, `S`. `Content` has `O`, `T`, `B`. Both are `StrEnum`s whose values are the lowercase letters.

## Hints

```python
Hints.parse("re,mu")            # Hints(preferences=(Hint.RE, Hint.MU))
Hints.parse(["ap", Hint.MU])    # strings and Hint members can be mixed
Hints.parse(None)               # empty Hints, which is falsy
```

`Hint` is a `StrEnum` with `RE`, `MU`, `PK`, `AP`, `CA`, `GS`. `hints.pick(candidates)` returns the first preference that appears in `candidates`, or `None`.

## plan() and execute()

Use these to inspect or reuse a conversion without running it immediately.

```python
from pathlib import Path
from vexy_pdfsvgpy import FormatSpec, Hints, plan, execute

steps = plan(FormatSpec.parse("svg"), FormatSpec.parse("png"), Hints.parse("mu"), options={"dpi": 96})
for step in steps:
    print(step.capability, step.backend.name, step.kwargs)
# svg_to_png pymupdf {'dpi': 96}

execute(steps, Path("logo.svg"), Path("logo.png"))
```

- `plan(input_spec, output_spec, hints=None, *, options=None) -> list[Step]` returns one `Step`. When both formats are the same it uses the normalize capability, without options. It raises `UnsupportedConversion` when no direct path exists, for example PNG to PNG or PDF to JPG.
- `execute(steps, src, dst) -> Path` runs the steps and returns `dst`. Exceptions from a backend that are not already `BackendFailure` are wrapped in `BackendFailure`.
- `Step` is a frozen dataclass with `capability`, `backend` and `kwargs`. `backend` has `name`, `hint` and `func`.
- `Capability` is the `StrEnum` of capability names listed in [Backends](backends.md#capability-table).

## Errors

All errors derive from `VexyError`.

| Class | Raised when |
|---|---|
| `InvalidInput` | A path is missing, a format spec or hint is invalid, an extension is unknown, or a directory has no matching files. |
| `UnsupportedConversion` | No backend is registered for the conversion. |
| `BackendFailure` | A backend raised. Attributes: `backend` (name), `op` (capability), `original` (the exception). The message reads `[backend] op failed: original`. |
| `UnsupportedOnPlatform` | Defined for platform-specific operations. The Apple backend currently reports non-macOS use through `BackendFailure` instead. |

```python
from vexy_pdfsvgpy import convert, VexyError

try:
    convert(input="scan.png", output="scan.png")
except VexyError as e:
    print(type(e).__name__, e)
# UnsupportedConversion identity conversion png → png is not supported
```

## Document and Page

`Document` and `Page` are passive containers for in-memory pages. `convert()` does not use them yet.

- `Page(content, kind, width, height, dpi=None, label=None)`. `content` is `bytes` for PDF and bitmaps and `str` for SVG. `width` and `height` are points for vector pages and pixels for bitmaps.
- `Document(pages=[], source=None, spec=None)` supports `len()`, `bool()`, `page_count`, `kind`, `add(page)`, `Document.empty(spec=None)` and `Document.from_path(path, *, spec=None)`. `from_path` does not read the file; it inserts one placeholder page so that `kind` is known.

## Reshape operations

`vexy_pdfsvgpy.operations.reshape` combines and splits documents directly, outside `convert()`:

| Function | Result |
|---|---|
| `pages2docs_pdf(src, out_dir, *, stem=None)` | One PDF per page, via `pikepdf`. Returns the list of paths. |
| `docs2pages_pdf(srcs, dst)` | One multi-page PDF, via `pikepdf`. |
| `docs2layers_pdf(srcs, dst, *, labels=None)` | One page with each source's first page in its own optional content group (OCG). Default labels: `Layer 1`, `Layer 2`, and so on. |
| `docs2layers_svg(srcs, dst, *, labels=None)` | One SVG with each source in an Inkscape layer: `<g inkscape:groupmode="layer" inkscape:label="...">`. Size and `viewBox` come from the first source. |
| `layers2docs_svg(src, out_dir)` | One SVG per Inkscape layer, named `{stem}-{label}.svg`. Falls back to top-level `<g>` elements when there are no Inkscape layers. |

```python
from pathlib import Path
from vexy_pdfsvgpy.operations import reshape

reshape.docs2layers_pdf(
    [Path("base.pdf"), Path("overlay.pdf")],
    Path("layered.pdf"),
    labels=["Base", "Overlay"],
)
```

## Other modules

- `vexy_pdfsvgpy.operations.regularize`: `regularize_pdf(src, dst, *, backend="pymupdf")` with `"pymupdf"` or `"apple"`, and `regularize_svg(src, dst, *, backend="pymupdf", width=2048)` with `"pymupdf"` or `"resvg"`. The `resvg` variant renders the SVG to PNG and wraps it as a base64 `<image>` in a new SVG.
- `vexy_pdfsvgpy.operations.color`: `ColorOptions`, `parse_color()` and `apply_color_bitmap()`. Not called by `convert()` yet.
- `vexy_pdfsvgpy.operations.sizecrop`: `SizeCropOptions`, `parse_dim()`, `resolve_dim()`, `compute_scale()`, `resolve_margins()`, `apply_sizecrop_pdf()`. Not called by `convert()` yet.
- `vexy_pdfsvgpy.paths`: `render_output(template, *, stem, page, ...)` fills `{stem}`, `{page}`, `{index}`, `{backend}`, `{ext}` and `{scale}` placeholders in an output path. It is not called by `convert()` yet.
