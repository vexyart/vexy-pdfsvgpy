---
this_file: SPEC.md
---

# vexy-pdfsvgpy — Specification

Unified Python library and Fire CLI for lossless, pure-pip PDF ⇄ SVG ⇄ PNG/JPG conversion. Every backend ships as a self-contained wheel; no Cairo, Poppler, Ghostscript, or system libs.

This document is the contract. It is derived from `IDEA.md` (qualifier grammar, ops, hints), `CLAUDE.md` (scope, backend rules), and `external/pdfsvgpy_demo.py` (the executable reference that already does 90% of this against `testdata/`).

---

## 1. Scope

One sentence: **convert between PDF, SVG, PNG, JPG with a declarative qualifier grammar, picking the right backend automatically, reusing one deterministic stack.**

In scope:

- Format conversions across the vector/bitmap graph: `pdf ⇄ svg ⇄ png/jpg`, plus `png → svg` (tracing) and `png/jpg → pdf/svg` (bitmap-in-vector wrapping).
- Multi-document handling: split multi-page PDFs, merge documents, promote pages to documents, demote documents to pages or layers.
- Operations: `--regularize` (round-trip normalization), `--dim` / size-and-crop, color ops (`--gray`, `--invert`, `--vivid`, `--bright`, `--contrast`, `--backdrop`).
- Tool hints: `re` (resvg), `mu` (pymupdf), `pk` (pikepdf), `ap` (Apple PDFKit/Quartz on macOS).
- Both a Python API (`vexy_pdfsvgpy` package) and a Fire CLI (`vexy-pdfsvgpy`).

Out of scope (explicit):

- Any backend requiring Cairo, Poppler, Ghostscript, libcairo, Skia, Inkscape, or external binaries.
- Enterprise bloat (circuit breakers, metrics, plugin systems, config frameworks). See `CLAUDE.md` §"no enterprise bloat".
- Edit-in-place semantic PDF manipulation (annotations, forms, OCR). This is a conversion tool, not an editor.
- True text-preserving PDF→SVG. PDF→SVG is inherently lossy — `text_as_path=True` is the only reliable path. Document the tradeoff in the API.

---

## 2. Backend stack (locked)

| Capability                    | Primary            | Alternate                    | Hint | Notes |
|-------------------------------|--------------------|------------------------------|------|-------|
| PDF → PNG                     | `pymupdf`          | `pypdfium2`, Quartz (`ap`)   | `mu` / `ap` | dpi= for pymupdf, scale=dpi/72 for pdfium |
| PDF → SVG                     | `pymupdf`          | —                            | `mu` | `page.get_svg_image(text_as_path=True)` always |
| SVG → PNG                     | `resvg-py`         | `pymupdf`                    | `re` / `mu` | resvg is higher fidelity; pymupdf handles pt→px natively |
| SVG → PDF                     | `pymupdf`          | —                            | `mu` | `pymupdf.open(svg).convert_to_pdf()` |
| PNG / JPG → SVG (trace)       | `vtracer`          | —                            | —    | `convert_image_to_svg_py(...)` |
| PNG / JPG → PDF (wrap)        | `pymupdf`          | `pikepdf`                    | —    | insert image on a new page |
| PNG / JPG → SVG (wrap, no trace) | builtin (base64 `<image>`) | — | — | fallback when tracing is wrong choice |
| PDF split                     | `pypdf`            | `pikepdf`, Quartz            | `pk` / `ap` | pikepdf is lossless; pypdf is pure-Python |
| PDF merge                     | `pikepdf`          | `pypdf`, Quartz              | `pk` / `ap` | pikepdf preserves structure |
| PDF normalize (regularize)    | `pymupdf`          | Quartz (`ap`)                | `mu` / `ap` | `doc.save(clean=True, deflate=True, garbage=4)` |
| SVG normalize (regularize)    | `pymupdf` round-trip | `resvg` raster-wrap fallback | `mu` / `re` | `get_svg_image(text_as_path=True)` |
| PDF layers (output OCGs)      | `pymupdf`          | `pikepdf` (flat overlay)     | `mu` / `pk` | `add_ocg()` + `show_pdf_page(..., oc=xref)` |
| SVG layers (output groups)    | `lxml` + backend   | —                            | —    | `<g inkscape:groupmode="layer">` |

**Forbidden backends** (do not import, do not add to `pyproject.toml`): `cairosvg`, `pdf2image`, `svglib`, `reportlab`, `Pillow` for PDF rendering, `skia-python`, `pdfkit`, `weasyprint`, anything needing Cairo/Poppler/Ghostscript. If a capability seems to require one, stop and re-read `IDEA.md`.

`Pillow` is allowed only for PNG/JPG metadata reads and re-encoding (no PDF involvement). `loguru` and `rich` are allowed for logging/CLI UX.

---

## 3. Format grammar (from `IDEA.md` §"Input and output file format support")

A format spec is `{format}-{packaging}{content}`.

**Formats:** `pdf`, `svg`, `png`, `jpg`.

**Packaging qualifiers (vector formats `pdf` / `svg`):**

| Code | Meaning                        | Notes |
|------|--------------------------------|-------|
| `d`  | collection of single-page files (DEFAULT) | one file per document |
| `m`  | multi-page file                | PDF only |
| `l`  | layered single-page file       | PDF: OCGs; SVG: `<g>` groups |
| `s`  | single-page file               | exactly one page |

**Packaging qualifiers (bitmap formats `png` / `jpg`):**

| Code | Meaning                        | Notes |
|------|--------------------------------|-------|
| `d`  | collection of files (DEFAULT)  | |
| `l`  | layered single-page file       | APNG for `png`; not supported for `jpg` |

**Content qualifiers (vector formats only):**

| Code | Meaning                          | Notes |
|------|----------------------------------|-------|
| `o`  | outlines (DEFAULT)               | text → path via `text_as_path=True` |
| `t`  | text, with embedded fonts if possible | attempt to preserve, best-effort |
| `b`  | bitmap-only                      | rasterize then wrap as image |

Either qualifier may be omitted when equal to the default. `pdf-mo` = multi-page PDF with outlines (the typical case). `svg-lt` = layered SVG with preserved text. `png` alone = `png-d`.

**Roles (CLI flags):**

- `--input` / `--output` — generic, picked as vector or bitmap from file extension.
- `--vinput` / `--voutput` — explicit vector.
- `--binput` / `--boutput` — explicit bitmap.

Routing rules (from IDEA.md §"roles"):

- Bitmap input with no vector input → wrap bitmap into a vector container first.
- Bitmap output with no vector output → route through an implied vector target, then rasterize.
- Vector-only → skip wrapping.

---

## 4. Tool hints

Single two-letter codes, lowercase:

- `re` — prefer resvg/usvg (implies SVG involvement).
- `mu` — prefer pymupdf (implies PDF involvement; default for most ops).
- `pk` — prefer pikepdf (implies PDF involvement; lossless priority).
- `ap` — prefer Apple PDFKit/Quartz (macOS only; falls back with warning on non-darwin).

CLI: `--hint re,mu` (comma-separated, order defines priority). API: `hints=("re", "mu")`.

Dispatch rule: find the first backend in the capability table whose key appears in the hint list. If none, use the primary.

---

## 5. Operations

### 5.1 Page and layer reshaping

Happens automatically when input and output packaging differ:

- `pages2docs` — multi-page input (`pdf-m`) → collection of docs. PDF: `pypdf.PdfWriter().add_page(p)` per page, or `pikepdf.Pdf.new(); one.pages.append(page)`.
- `docs2pages` — collection → multi-page PDF. `pikepdf.Pdf.new(); merged.pages.extend(...)` (lossless) or `pypdf.PdfWriter()` (pure-Python).
- `layers2docs` — layered PDF: toggle each OCG via `set_layer_ui_config` and re-render per layer. Layered SVG: parse with `lxml`, split on `<g inkscape:groupmode="layer">`. APNG → one doc per frame.
- `docs2layers` — PDF output: `pymupdf.add_ocg()` + `page.show_pdf_page(..., oc=ocg_xref)` stacking onto one page. SVG output: build a parent `<svg>` and wrap each doc's children in `<g id="layerN" inkscape:groupmode="layer" inkscape:label="...">`.

See IDEA.md §"Pages and layers to documents" and §"Documents to pages and layers" for the exact code patterns. `docs2layers` requires uniform dimensions — run size-and-crop first.

### 5.2 `--regularize`

Pass-through canonicalization:

- **SVG input** → `pymupdf.open(svg).single_page.get_svg_image(text_as_path=True)`. Fallback: `_resvg_render(src, width=2048)` + base64 `<image>` wrap, if the pymupdf round-trip fails (e.g. exotic SVG features).
- **PDF input** → `doc.save(out, clean=True, deflate=True, garbage=4)`. With hint `ap` on macOS: `PDFDocument.alloc().initWithURL_(url); doc.writeToFile_(out)`.

### 5.3 `--dim` / size-and-crop

Harmonize the visible area of all documents to a target dimension.

**`--dim`** (default `none`):

- `none` — skip size-and-crop entirely.
- `largest` / `first` / `last` — pick from the input document set.
- `WWWWxHHHH` — explicit pixels (interpreted as PDF units at 72dpi for vector targets).

When `--dim` is given, every document gets a transparent rectangle sized to the target dimension regardless of scaling and cropping (so the final page box is deterministic).

**`--scale`** (default `fit`):

- `fit` — preserve aspect, fit within target.
- `keep` — do not scale.
- `NNN` — literal percentage.
- `width` / `height` — fit one axis, adapt the other.

**Alignment:** `--top`, `--bottom`, `--left`, `--right`, each `NNN%` or `auto`. CSS margin semantics: if top is given, bottom is auto; if left is given, right is auto.

**`--crop`** (default `all`):

- `all` — crop and pad to exactly target dim.
- `keep` — no crop, no pad.
- `width` — crop only over-wide.
- `height` — crop only over-tall.
- `down` — crop both dimensions only when exceeding target.

### 5.4 Color operations

Applied after size-and-crop, before final encoding. For vector outputs, ops that cannot be expressed in SVG/PDF filters are applied in the rasterization step (post-render, pre-re-vectorize). For bitmap outputs, applied via Pillow on the rendered image.

- `--gray` (bool) — convert to grayscale.
- `--invert` (bool) — invert channels.
- `--vivid N` — increase saturation by `N` (linear multiplier on HSV S; 0 = no change).
- `--bright N` — brightness delta; negative darkens.
- `--contrast N` — contrast delta; negative softens.
- `--backdrop COLOR` — fill behind the page with `COLOR`. Accepts `#rrggbb`, `#rrggbbaa`, `white`, `black`, `dominant`. `dominant` rasterizes, samples the most frequent color, uses that.

---

## 6. Architecture

`src/vexy_pdfsvgpy/` layout:

```
__init__.py          — public API re-exports
types.py             — FormatSpec, Packaging, Content, Role, Hint enums and dataclasses
document.py          — Document and Page in-memory intermediate types
paths.py             — file path parsing and naming ({stem}-via-{backend}@{scale}.{ext})
dispatch.py          — capability table, hint resolution, pipeline planning
pipeline.py          — ordered list of steps that convert input to output
backends/
  __init__.py        — Backend protocol / ABC
  pymupdf_backend.py — all pymupdf ops
  pdfium_backend.py  — PDF → PNG via pypdfium2
  resvg_backend.py   — SVG → PNG via resvg-py (with pt→px fallback)
  pypdf_backend.py   — split/merge via pypdf
  pikepdf_backend.py — split/merge/layers via pikepdf
  vtracer_backend.py — PNG/JPG → SVG
  apple_backend.py   — Quartz/PDFKit on darwin (optional import)
  wrap_backend.py    — base64-<image> SVG wrapping; bitmap embedded in PDF
operations/
  reshape.py         — pages2docs, docs2pages, layers2docs, docs2layers
  regularize.py      — SVG/PDF canonicalization
  sizecrop.py        — --dim, --scale, margins, --crop
  color.py           — --gray, --invert, --vivid, --bright, --contrast, --backdrop
cli.py               — Fire CLI entry point
```

**Design rules** (from `CLAUDE.md`):

1. **Parse, don't validate at the boundary.** `FormatSpec.parse("pdf-mo")` returns a typed object; internals only accept typed objects.
2. **One engine per capability.** `dispatch.resolve(cap, hints)` returns exactly one `Backend`. No ambiguity in inner code.
3. **Errors as data at the API boundary.** Narrow exceptions: `UnsupportedConversion`, `BackendFailure`, `InvalidInput`. Never leak `fitz.FileDataError` or `pikepdf.PdfError` to callers.
4. **Intermediate `Document` type.** Every conversion is `Input → Document → Output`. `Document` holds typed pages as either PDF bytes, SVG strings, or bitmap tensors (Pillow `Image`), plus per-page metadata (dimensions, origin, layer name). Backends consume and produce `Document`s.
5. **Flat functions over classes.** `Manager`/`Handler`/`Framework` names are banned per CLAUDE.md §6.

**Pipeline planning** (`dispatch.plan`):

```
plan(input_spec, output_spec, hints) -> list[Step]
```

A `Step` is `(capability, backend, kwargs)`. Example: `("svg → png", resvg_backend, {"width": 2048})`.

Rules:

1. If `input.format == output.format` and only packaging/qualifier differs → reshape only.
2. Else: vector-in → vector-out is one step; vector-in → bitmap-out is vector-convert + rasterize; bitmap-in → vector-out is trace-or-wrap + vector-convert.
3. Reshape ops (`pages2docs`, `docs2layers`, etc.) are inserted based on packaging mismatch.
4. `--regularize` inserts a normalization step at the vector layer boundary.
5. Size-and-crop and color ops are inserted after vector conversion, before rasterization (or at the final step if output is vector).

---

## 7. Public API

```python
from vexy_pdfsvgpy import convert, FormatSpec, Hints, Document

# Simple path → path
convert(
    input="coupon.pdf",
    output="coupon-{page:02d}.png",
    hints="mu",
    dim="2048x0",
    regularize=True,
)

# Explicit format specs
convert(
    vinput="design.svg",
    voutput="design-norm.svg",
    regularize=True,
    hints=("re", "mu"),
)

# API primitives
spec = FormatSpec.parse("pdf-mo")
doc = Document.load("in.pdf")
doc = regularize(doc, hints=Hints(("mu",)))
doc.save("out.pdf", spec=spec)
```

Exactly one public entry point — `convert()` — plus the primitives (`FormatSpec`, `Document`, `Hints`, `convert_document`, the operation functions). No global state, no config files, no plugin registry.

---

## 8. CLI (`vexy-pdfsvgpy`, built on Fire)

```
vexy-pdfsvgpy convert \
  --input IN [--output OUT] \
  [--vinput V] [--voutput V] [--binput B] [--boutput B] \
  [--hint re,mu] \
  [--regularize] \
  [--dim none|largest|first|last|WxH] \
  [--scale fit|keep|NNN|width|height] \
  [--top N|auto] [--bottom N|auto] [--left N|auto] [--right N|auto] \
  [--crop all|keep|width|height|down] \
  [--gray] [--invert] [--vivid N] [--bright N] [--contrast N] \
  [--backdrop COLOR] \
  [--verbose]
```

Subcommands: `convert` (everything), `split`, `merge`, `regularize` (shortcuts that are just `convert` presets). `--verbose` turns on `loguru` DEBUG. Rich tables for progress and result summary.

Output filename templating supports `{stem}`, `{page}`, `{index}`, `{backend}`, `{ext}`. Default when input is multi-page and output has no template: append `-p{page:02d}` before extension.

---

## 9. Error model

```python
class VexyError(Exception): ...
class InvalidInput(VexyError): ...               # bad path, bad FormatSpec, unreadable file
class UnsupportedConversion(VexyError): ...      # no backend can handle this graph edge
class BackendFailure(VexyError): ...             # backend raised; wrapped with backend name + original message
class UnsupportedOnPlatform(VexyError): ...      # `ap` hint on non-darwin
```

Never leak `fitz.*`, `pikepdf.*`, `pypdfium2.*`, `vtracer.*`, `resvg_py.*` exception types. Wrap at the backend boundary, include backend name and op.

---

## 10. Testing and verification strategy

**Unit tests** (`tests/`, pytest via `hatch test`):

- `test_format_spec.py` — parse every valid combo in the qualifier grammar, round-trip via `__str__`, reject invalid inputs with `InvalidInput`.
- `test_dispatch.py` — capability table covers the full conversion graph; hint resolution picks the right backend in priority order; `UnsupportedConversion` raised for impossible edges.
- `test_paths.py` — filename templating.
- `test_operations_reshape.py` — `pages2docs`/`docs2pages` round-trip yields byte-identical page count; `docs2layers` produces OCGs on output.
- `test_operations_sizecrop.py` — dim resolution, CSS-margin semantics, all `--scale` modes.
- `test_operations_color.py` — grayscale, invert, dominant backdrop detection.

**Backend adapter tests** — real calls, no mocks. Each backend gets a test that exercises its real API against a tiny fixture from `testdata/`. Skip decorated on `ImportError` only (every Tier-1 backend is a required dep; skipping should never fire). `apple_backend` tests skip on non-darwin.

**Integration tests** (`tests/test_real_world.py`) — for each fixture in `testdata/`, run the full conversion graph: pdf→png, pdf→svg, svg→pdf, svg→png, png→svg, split(fontlab_posters.pdf), merge. Assert the output files exist and are non-empty. For bitmap outputs, assert Pillow can open them and dimensions are sane.

**Examples as functional tests** (`examples/`) — runnable scripts with `#!/usr/bin/env -S uv run -s` headers that demonstrate real use and also serve as acceptance tests:

- `examples/convert_coupon.py` — split `fontlab_posters.pdf`, rasterize each page at 300dpi, re-merge.
- `examples/trace_logo.py` — trace `svglogo.svg` → png → svg via vtracer.
- `examples/layer_stack.py` — build a layered PDF from three SVGs.
- `examples/regularize_batch.py` — run `--regularize` on every fixture.

**Reference parity test** — `tests/test_demo_parity.py` invokes the equivalent library operations and compares file sizes / pixel dimensions against the outputs `external/pdfsvgpy_demo.py` wrote into `out/`. Not byte-identical (deflation is non-deterministic) but order-of-magnitude sanity.

**Real-world smoke**:

```bash
uv run vexy-pdfsvgpy convert --input testdata/fontlab_posters.pdf --output /tmp/posters.svg --hint mu
uv run vexy-pdfsvgpy convert --input testdata/hello_glyphs.svg --output /tmp/hello.pdf --regularize
uv run vexy-pdfsvgpy convert --input testdata/tiger.svg --output /tmp/tiger.png --dim 2048x2048
```

Run these manually on every phase boundary. If any fails, the phase isn't done.

---

## 11. Implementation process

**Phase 0 — Bootstrap (<30 min).** `pyproject.toml` (hatch-vcs, ruff, mypy, pytest), `uv sync`, empty package skeleton, `this_file` markers, pre-commit hook or `test.sh` wrapper. Single smoke test that imports the package.

**Phase 1 — Types and grammar (~1h).** `FormatSpec`, `Packaging`, `Content`, `Role`, `Hint` as enums/dataclasses. Parser in `types.py`. Full unit tests. Round-trip property tests.

**Phase 2 — Document intermediate and path helpers (~1h).** `Document` holds ordered pages and metadata. `Document.load(path, spec)` dispatches on extension. `paths.render_output(template, **vars)` produces the final filename. Tests.

**Phase 3 — Backends, one at a time, verified against `testdata/` (~4-6h).**

1. `pymupdf_backend` — PDF ⇄ SVG ⇄ PDF, PDF → PNG, PDF normalize. Verify against `testdata/fontlab_posters.pdf` and `hello_glyphs.svg`.
2. `pdfium_backend` — PDF → PNG. Verify against `testdata/papercut.pdf`.
3. `resvg_backend` — SVG → PNG with pt→px fallback. Verify against `testdata/tiger.svg`.
4. `pypdf_backend` — split, merge. Verify splits `regularity.pdf` into the right page count.
5. `pikepdf_backend` — split, merge, overlay. Verify.
6. `vtracer_backend` — PNG/JPG → SVG. Verify trace on a pymupdf rendering.
7. `apple_backend` — darwin-only. Verify on macOS.
8. `wrap_backend` — base64 `<image>` SVG and bitmap-in-PDF. No external deps.

After each backend, run `uvx hatch test` and write an `examples/` script that uses it end-to-end. Don't start the next backend until the previous is green.

**Phase 4 — Dispatch and pipeline (~2h).** Capability table from backends, `plan()`, `execute()`. Tests cover every graph edge. End-to-end: `convert(input=..., output=...)` works.

**Phase 5 — Reshape ops (~2h).** `pages2docs`, `docs2pages`, `layers2docs`, `docs2layers`. Each op is a pure function over `Document`. Tests on multi-page fixtures.

**Phase 6 — Regularize, size-and-crop, color (~3h).** One module per family. Integration test: `convert(..., regularize=True, dim="2048x2048", gray=True)` produces a sensible result on every fixture.

**Phase 7 — CLI (~1h).** Fire wrapper around `convert()`. Rich output. Filename templating. Smoke-test all three sample CLI invocations from §10.

**Phase 8 — Examples, docs, polish (~1h).** `examples/*.py`, `README.md` (<200 lines per CLAUDE.md), `CHANGELOG.md`, `DEPENDENCIES.md`, `WORK.md`.

**Iteration loop (per phase)**:

1. Write the failing test first (red).
2. Implement the minimum code to pass (green).
3. Run the full post-edit chain from CLAUDE.md §"commands".
4. Read the diff line-by-line — would a senior reviewer call it overcomplicated?
5. Update `WORK.md` with what got done and what broke.
6. Move to the next phase only when tests are green AND a real `uv run` CLI invocation succeeds against `testdata/`.

**Real-life verification** after each backend is wired:

```bash
uv run python -c "from vexy_pdfsvgpy import convert; convert(input='testdata/fontlab_posters.pdf', output='/tmp/out.png')"
```

If the output doesn't render in Preview.app or Chrome, the phase isn't done.

**Reviewing and refining** at phase boundaries:

- Delete first, add second. Every `Manager`/`Handler` class name gets renamed or removed.
- Any file over 200 lines gets split.
- Any function over 20 lines gets decomposed unless it's a linear pipeline.
- Run `uvx mypy src/vexy_pdfsvgpy/` — no errors.
- Run `uvx ruff check --select ALL src/vexy_pdfsvgpy/` — triage.
- Re-read `IDEA.md` §"Tool hints" and §"size-and-crop" — is the implementation faithful?

---

## 12. Acceptance criteria

The library ships when:

1. `uv sync && uvx hatch test` is green on a clean clone on macOS, Linux, and Windows (CI runs all three).
2. Every operation in §5 has at least one unit test and one real-data integration test.
3. Every backend adapter in §2 has a test that invokes its real API against a `testdata/` fixture.
4. `convert()` handles the full graph edge set in §6 (pdf↔svg↔png, pdf↔jpg, svg↔png, svg↔jpg, png↔svg, plus bitmap-wrap and bitmap-trace variants).
5. `--regularize`, `--dim`, `--scale`, `--crop`, every color op works end-to-end on at least one fixture per op.
6. The Fire CLI runs the three smoke invocations in §10 without error on a fresh install.
7. `README.md` shows install + one CLI example + one Python example, under 200 lines.
8. `DEPENDENCIES.md` lists every dep with a one-line "why this, not X" justification.
9. Zero imports from `cairosvg`, `pdf2image`, `svglib`, `reportlab`, `skia-python`, `pdfkit`, `weasyprint`. Grep confirms.
10. `fd -e py src/ -x wc -l {} \;` shows no file over 200 lines; no function over 40 lines.
