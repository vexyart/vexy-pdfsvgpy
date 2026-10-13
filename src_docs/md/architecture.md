# Architecture

`vexy-pdfsvgpy` is a thin layer over a fixed set of backends. A call passes through four stages: parse the formats, plan, dispatch, execute.

```text
convert(input, output, ...)
   │
   ├─ FormatSpec.parse / from_extension   →  input_spec, output_spec
   ├─ Hints.parse                          →  hints
   ├─ _gather_inputs                       →  [file, ...]
   │
   └─ for each file:
        plan(input_spec, output_spec, hints, options)
           └─ dispatch.resolve(capability, hints)  →  BackendFn
        execute(steps, src, dst)
           └─ backend.func(src, dst, **kwargs)
```

## Source layout

| Module | Role |
|---|---|
| `vexy_pdfsvgpy/__init__.py` | `convert()`, input gathering, public exports |
| `types.py` | `FormatSpec`, `Packaging`, `Content`, `Hint`, `Hints` |
| `pipeline.py` | `plan()`, `execute()`, `Step` |
| `dispatch.py` | `Capability`, the backend table, `resolve()` |
| `backends/` | One module per library: `pymupdf_backend`, `pdfium_backend`, `resvg_backend`, `pypdf_backend`, `pikepdf_backend`, `vtracer_backend`, `wrap_backend`, `apple_backend`, `cairo_backend`, `ghostscript_backend` |
| `operations/` | `reshape`, `regularize`, `sizecrop`, `color` |
| `document.py` | `Document`, `Page` |
| `paths.py` | Output file name templating |
| `errors.py` | `VexyError` and subclasses |
| `cli.py` | The Fire `CLI` class and `main()` |

## Follow one call

Take `convert(input="logo.svg", output="logo.png", hints="mu", dpi=96)`.

1. **Parse.** No `vinput` or `binput` is given, so `FormatSpec.from_extension("logo.svg")` returns `svg` (packaging `d`, content `o`). The output becomes `png` (packaging `d`). `Hints.parse("mu")` returns `(Hint.MU,)`.
2. **Gather.** The input is a file, so the list is `[Path("logo.svg")]`.
3. **Plan.** The formats differ, so `plan()` looks up `("svg", "png")` in its table of direct conversions and finds `Capability.SVG_TO_PNG`.
4. **Dispatch.** `resolve()` reads the backends for `svg_to_png`: `resvg` (`re`), `pymupdf` (`mu`), `cairo` (`ca`). The first hint, `mu`, matches `pymupdf`, so the step uses `pymupdf_backend.svg_to_png`.
5. **Execute.** `execute()` calls `svg_to_png(Path("logo.svg"), Path("logo.png"), dpi=96)`. The backend renders the SVG with PyMuPDF and saves the PNG.
6. **Return.** `convert()` returns `Path("logo.png")`.

Without `hints="mu"`, step 4 picks `resvg`, and `dpi=96` fails in step 5 because `resvg_backend.svg_to_png` takes `width`, not `dpi`.

## Planning

`plan()` knows two kinds of conversion:

- **Same format** (`pdf`→`pdf`, `svg`→`svg`): the normalize capability for that format. Options are not forwarded. PNG→PNG and JPG→JPG raise `UnsupportedConversion`.
- **Direct conversion**, one step:

| From | To | Capability |
|---|---|---|
| `pdf` | `png` | `pdf_to_png` |
| `pdf` | `svg` | `pdf_to_svg` |
| `svg` | `pdf` | `svg_to_pdf` |
| `svg` | `png` | `svg_to_png` |
| `png`, `jpg` | `svg` | `png_to_svg_trace` |
| `png`, `jpg` | `pdf` | `bitmap_to_pdf` |

Any other pair raises `UnsupportedConversion`, for example `pdf`→`jpg` or `svg`→`jpg`. JPG is accepted as an input but no conversion writes JPG yet.

`execute()` accepts several steps and writes intermediate files next to the destination as `<dst>.step<i>.tmp`. `plan()` currently returns one step only.

## Dispatch

`dispatch._load_table()` imports each backend module inside `try`/`except ImportError` and registers its functions. A missing optional library therefore does not break `import vexy_pdfsvgpy`. The table is built on first use and cached.

`resolve(cap, hints)`:

1. Gets the backend list for the capability. If it is empty, raises `UnsupportedConversion`.
2. For each hint in order, returns the first backend with that hint.
3. Otherwise returns the first backend in the list.

## Error handling

Backends raise `RuntimeError` with a `[backend]` prefix. `execute()` wraps anything that is not already a `BackendFailure` as `BackendFailure(backend.name, capability, original)`. The CLI catches `VexyError`, prints the class name and message, and returns exit code `1`.

## Design rules

These rules come from `SPEC.md` and `IDEA.md` in the repository:

- Every default backend installs as a wheel with no system library and no post-install step.
- One backend per capability by default. Alternatives exist only where a real trade-off is worth exposing, and you choose them with a hint, not a configuration file.
- Inputs are parsed into typed objects (`FormatSpec`, `Hints`) at the boundary.
- Backend exceptions do not leak; they are wrapped in the narrow `VexyError` hierarchy.
- No global configuration, plugin registry or caching layer beyond the dispatch table.
