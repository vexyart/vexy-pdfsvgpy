---
this_file: WORK.md
---

# Work log

## Phase 8 — Examples and documentation (complete, 2026-04-14)

### Done
- Created `examples/convert_coupon.py`: split PDF, rasterize pages at 300dpi, re-merge
- Created `examples/trace_logo.py`: SVG → PNG → traced SVG round-trip
- Created `examples/layer_stack.py`: stack SVGs into layered PDF (OCGs) and layered SVG
- Created `examples/regularize_batch.py`: batch regularize all fixtures with Rich table
- Created `README.md` (<200 lines): install, quick start, format grammar, backend table, rejected backends
- Updated `CHANGELOG.md`: prepended Phase 1-8 entry
- Updated `DEPENDENCIES.md`: expanded runtime table with rationale column
- Updated `WORK.md`: final pass

## Phase 7 — CLI (complete)

### Done
- `src/vexy_pdfsvgpy/cli.py`: Fire CLI with `convert`, `split`, `merge`, `regularize` subcommands
- `--verbose` turns on loguru DEBUG; Rich table summarises output

## Phase 6 — Regularize, size-and-crop, color (complete)

### Done
- `src/vexy_pdfsvgpy/operations/regularize.py`: PDF (pymupdf clean-save) and SVG (round-trip or resvg raster-wrap)
- `src/vexy_pdfsvgpy/operations/sizecrop.py`: `resolve_dim`, `apply_scale`, `apply_margins`, `apply_crop`
- `src/vexy_pdfsvgpy/operations/color.py`: `apply_color` with `gray`, `invert`, `vivid`, `bright`, `contrast`, `backdrop`

## Phase 5 — Reshape operations (complete)

### Done
- `src/vexy_pdfsvgpy/operations/reshape.py`: `pages2docs_pdf`, `docs2pages_pdf`, `docs2layers_pdf` (OCGs), `docs2layers_svg` (Inkscape layers), `layers2docs_svg`

## Phase 4 — Dispatch and pipeline (complete)

### Done
- `src/vexy_pdfsvgpy/dispatch.py`: `Capability` StrEnum, `CAPABILITY_TABLE`, `resolve()`
- `src/vexy_pdfsvgpy/pipeline.py`: `Step`, `plan()`, `execute()`
- `src/vexy_pdfsvgpy/__init__.py`: public `convert()` entry point

## Phase 3 — Backend adapters (complete)

### Done
- `pymupdf_backend`: PDF→PNG, PDF→SVG, SVG→PDF, SVG→PNG, PDF normalize, SVG normalize
- `pdfium_backend`: PDF→PNG via pypdfium2
- `resvg_backend`: SVG→PNG with pt-unit fallback
- `pypdf_backend`: split, merge
- `pikepdf_backend`: split, merge, overlay
- `vtracer_backend`: PNG/JPG→SVG trace
- `apple_backend`: macOS PDFKit/Quartz (darwin-only, skipped elsewhere)
- `wrap_backend`: PNG→SVG base64 wrap, bitmap→PDF

## Phase 2 — Document intermediate and path helpers (complete)

### Done
- `src/vexy_pdfsvgpy/document.py`: `Page`, `Document`, `Document.load()`
- `src/vexy_pdfsvgpy/paths.py`: `render_output()` with filename templating

## Phase 1 — Format grammar and types (complete)

### Done
- `src/vexy_pdfsvgpy/types.py`: `Packaging`, `Content`, `Role`, `Hint`, `FormatSpec`, `Hints`
- `src/vexy_pdfsvgpy/errors.py`: `VexyError`, `InvalidInput`, `UnsupportedConversion`, `BackendFailure`, `UnsupportedOnPlatform`

## Phase 0 — Bootstrap (complete)

### Done
- Created `pyproject.toml` with hatch-vcs, ruff, mypy, pytest config
- Created `src/vexy_pdfsvgpy/__init__.py`, `cli.py`, `py.typed`
- Created `tests/__init__.py`, `tests/test_smoke.py`
- Created `test.sh` executable
- Created `WORK.md`, `CHANGELOG.md`, `DEPENDENCIES.md`
