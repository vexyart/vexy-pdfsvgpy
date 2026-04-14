---
this_file: TODO.md
---

# vexy-pdfsvgpy — Task list

Flat, itemized view of `SPEC.md` §11. Implementation order is top-to-bottom; each phase is a gate — do not start the next until its tests and real-life verification pass. Every task ends with `verify:` — the concrete check that proves it's done.

## Process rules (read first)

- [ ] Test-first for every task (red → green → refactor). Use `pytest` in `tests/`.
- [ ] After every edit, run the post-edit chain from `CLAUDE.md` §"commands" (autoflake, pyupgrade, ruff check, ruff format, hatch test).
- [ ] Update `WORK.md` at the start and end of each phase: what is in flight, what just got done, what broke.
- [ ] Tick off these boxes in `TODO.md` as you go. Move completed phases into `CHANGELOG.md`.
- [ ] No file over 200 lines, no function over 40 lines. If a task produces one, split it before ticking the box.
- [ ] Zero imports from the forbidden backend list in `SPEC.md` §2. Grep before committing.
- [ ] Never edit anything under `external/`. Read-only reference.

---

## Phase 0 — Bootstrap ✅ complete

- [x] Create `pyproject.toml` with `[project]`, `[build-system]` (`hatchling`+`hatch-vcs`), `[tool.hatch.version]` (`source = "vcs"`), `[tool.hatch.build.targets.wheel] packages = ["src/vexy_pdfsvgpy"]`, `[tool.ruff]`, `[tool.mypy]`, `[tool.pytest.ini_options]`, `[tool.hatch.envs.default] dependencies = [...]`. Deps: `pymupdf`, `pypdfium2`, `pypdf`, `pikepdf`, `resvg-py`, `vtracer`, `Pillow`, `lxml`, `fire`, `loguru`, `rich`. Dev deps: `pytest`, `pytest-cov`, `mypy`, `ruff`. Python `>=3.12`. Script: `vexy-pdfsvgpy = "vexy_pdfsvgpy.cli:main"`.
- [x] Create `src/vexy_pdfsvgpy/__init__.py` with `__version__` from `hatch_vcs` and a top docstring. Add the `this_file` marker comment.
- [x] Create `src/vexy_pdfsvgpy/py.typed` (empty) so downstream gets inline types.
- [x] Create `tests/__init__.py` and `tests/test_smoke.py` that imports `vexy_pdfsvgpy` and asserts `__version__` is a non-empty string.
- [x] Create `test.sh` executable script that runs the full post-edit chain.
- [x] Run `uv venv --python 3.12 --clear && uv sync`. verify: `uvx hatch test` is green on the smoke test. **Version: `0.0.2.dev0+g946df4f62.d20260414`**
- [x] Create empty `WORK.md`, `CHANGELOG.md`, `DEPENDENCIES.md`. Leave `README.md` for Phase 8. verify: files exist.

## Phase 1 — Format grammar and types ✅ complete (63 tests)

- [x] `types.py`: `Packaging`, `Content`, `Hint` StrEnums; `FormatSpec` frozen dataclass with `parse()`, `from_extension()`, `__str__`, `is_vector`, `is_bitmap`; `Hints` frozen dataclass with `parse()`, `pick()`, `__bool__`.
- [x] `errors.py`: `VexyError`, `InvalidInput`, `UnsupportedConversion`, `BackendFailure`, `UnsupportedOnPlatform`.
- [x] `tests/test_types.py`: 63 tests covering valid/invalid FormatSpec parsing, round-trip, `from_extension`, `is_vector`/`is_bitmap`, `Hints.parse`/`pick`, `BackendFailure.__str__`. Green on Python 3.12, 3.13, 3.14.

## Phase 2 — Document intermediate and path helpers ✅ complete (30 tests)

- [x] `document.py`: `Page` (content/kind/width/height/dpi/label), `Document` (pages, source, spec), `Document.empty`, `Document.from_path` (extension-inferred spec, placeholder page). 88 lines.
- [x] `paths.py`: `render_output()` with `{stem}`, `{page}`, `{backend}`, `{scale}`, `{ext}` placeholders; auto-pagination for multi-page outputs; `parse_scale_suffix()`, `ensure_parent()`. 115 lines.
- [x] `tests/test_document.py` — 9 tests, smoke output `source: regularity.pdf spec: pdf pages: 1`.
- [x] `tests/test_paths.py` — 21 tests covering all placeholders and auto-pagination.

## Phase 3 — Backend adapters ✅ complete (47 tests across 8 backends)

Decision: backends are **file-based** (`src: Path, dst: Path`), not `Document`-based. Simpler than the original SPEC and matches the reference demo. Dispatcher threads a `Document` carrying a source path through backend calls.

- [x] **3.1 pymupdf_backend** (130 lines, 9 tests) — `pdf_to_png`, `pdf_to_svg`, `svg_to_pdf`, `svg_to_png`, `pdf_normalize`, `svg_normalize`, `pdf_page_count`, `pdf_page_size`. Always closes docs in `try/finally`. Wraps all exceptions as `RuntimeError("[pymupdf] ...")`. Quirk: `pymupdf.FileNotFoundError` must be caught at `_open()` helper, not in per-op bodies.
- [x] **3.2 pdfium_backend** (64 lines, 4 passed + 1 skipped) — `pdf_to_png` via `pdfium.PdfDocument(...).render(scale=dpi/72)`. DPI scaling is exact (ratio 4.1672 vs 4.1667 expected).
- [x] **3.3 resvg_backend** (77 lines, 7 tests) — `svg_to_png` via `resvg_py.svg_to_bytes`, with pt→px unit-rewrite fallback for Cairo/FontLab SVGs. Current resvg version handles pt natively; fallback is in place regardless.
- [x] **3.4 pypdf_backend** (7 tests) — pure-Python `split`, `merge`, `pdf_page_count`. Split 54-page `regularity.pdf`, merge round-trip preserves count.
- [x] **3.5 pikepdf_backend** (119 lines, 7 tests) — lossless `split`, `merge`, `overlay_pages` (Form XObjects). Quirk: `copy_foreign` on a `Page` raises `NotImplementedError`; pass `pdf.pages[0]` directly to `add_overlay`. Close ordering critical — sources stay open until after `save()`.
- [x] **3.6 vtracer_backend** (50 lines, 5 tests) — `trace(png, svg)` via `vtracer.convert_image_to_svg_py`. Quirk: `pyo3_runtime.PanicException` inherits from `BaseException`, not `Exception`; backend catches `BaseException` to guarantee `[vtracer]` prefix.
- [x] **3.7 apple_backend** (162 lines, 7 tests) — macOS-only `pdf_normalize`, `split`, `merge`, `pdf_to_png`, `pdf_page_count` via PDFKit + CoreGraphics. Lazy-imports `Foundation`/`Quartz` inside function bodies so module imports cleanly on Linux/Windows. Raster uses CTM translate + scale + white-fill context per the demo.
- [x] **3.8 wrap_backend** (80 lines, 7 tests) — `png_to_svg`/`jpg_to_svg`/`bitmap_to_svg` (base64 `<image>` in a minimal SVG), `png_to_pdf` (pymupdf opens raster directly, `convert_to_pdf()` returns PDF bytes). Output starts with `%PDF-1.7`.

## Phase 4 — Dispatch and pipeline ✅ complete (22 tests)

- [x] `dispatch.py` — `Capability` StrEnum, `BackendFn` dataclass, `capability_table()` lazy loader (tolerates missing backends), `resolve(cap, hints)` with hint priority. 120 lines. resvg inserted at front of `SVG_TO_PNG` so it's default; pikepdf at front of `PDF_MERGE`.
- [x] `pipeline.py` — `Step` dataclass, `plan()` with direct-conversion map and same-format normalize, `execute()` threading single-step pipelines. 80 lines.
- [x] `__init__.py` — replaced stub with full public API (`convert`, `FormatSpec`, `Document`, `Hints`, `Capability`, error types, `plan`, `execute`). `convert()` infers specs from file extensions, parses hints string, calls plan/execute.
- [x] `tests/test_dispatch.py` (7 tests), `tests/test_pipeline.py` (8 tests), `tests/test_convert.py` (7 tests) — 22 total green. Smoke: pdf→png 247,212 B, svg→pdf 45,868 B, svg→png 971,285 B.
- [x] Decision: `pdf_split`/`pdf_merge`/`pdf_page_count` are in dispatch table but skipped by `plan()` because their signatures don't match the `(src, dst)` pipeline thread contract — reserved for dedicated API.

## Phase 5 — Reshape operations ✅ complete (7 tests)

- [x] `operations/reshape.py` — `pages2docs_pdf` (delegates to pikepdf.split), `docs2pages_pdf` (delegates to pikepdf.merge), `docs2layers_pdf` (pymupdf `add_ocg` + `show_pdf_page` stacking), `docs2layers_svg` (lxml `<g inkscape:groupmode="layer">`), `layers2docs_svg` (reverse split). All lazy-import backends, file-based.
- [x] `tests/operations/test_reshape.py` — smoke confirms split=5 pages, OCGs `{'P1','P2','P3'}`, layered SVG 177KB, split SVG round-trip yields 2 files.
- [x] Quirk: `hello_glyphs.svg` has no width/height (only viewBox); fallback to 800/600 documented. OCG dict keys are xrefs (ints), not names — tests introspect via `v["name"]`.

## Phase 6 — Regularize, size-and-crop, color ✅ complete (25 tests)

- [x] `operations/regularize.py` — `regularize_pdf(src, dst, backend="pymupdf"|"apple")`, `regularize_svg(src, dst, backend="pymupdf"|"resvg", width=2048)`. resvg path renders to PNG then wraps as base64 `<image>` SVG.
- [x] `operations/sizecrop.py` — `SizeCropOptions` dataclass; `parse_dim`, `resolve_dim` (`none`/`first`/`last`/`largest`/`WxH`), `compute_scale` (`fit`/`keep`/`width`/`height`/`NNN%`), `resolve_margins` (CSS-auto), `apply_sizecrop_pdf` using pymupdf `new_page` + `show_pdf_page`.
- [x] `operations/color.py` — `ColorOptions`, `parse_color` (`#rrggbb`/`#rrggbbaa`/named/`dominant` via 64×64 resize sampling), `apply_color_bitmap` using Pillow `ImageOps`/`ImageEnhance`.
- [x] 25 tests across regularize, sizecrop, color. Smoke: regularized pdf 1.12MB, sized pdf 14.8MB, color out 108B. `bright`/`contrast` scale: `-100..100` → Pillow factor `0..2`.

## Phase 7 — CLI ✅ complete (7 tests)

- [x] `cli.py` (138 lines) — Fire-based `CLI` class with `version`, `convert`, `regularize`, `split`, `merge` subcommands. Rich tables for output summary. `--verbose` configures loguru DEBUG.
- [x] `__main__.py` — enables `python -m vexy_pdfsvgpy`.
- [x] Options dict builds only non-None/non-False values before forwarding to `convert()`.
- [x] Fire quirk fixed: wraps `fire.Fire(CLI)` with `sys.exit(result)` so return codes propagate.
- [x] `tests/test_cli.py` (7 tests) — subprocess invocations against real fixtures. Verified: version prints, pdf→png 247KB, svg→pdf 45KB, svg→png 971KB via `--hint mu`.

## Phase 8 — Examples, docs, polish ✅ complete

- [x] `examples/convert_coupon.py` — splits `fontlab_posters.pdf` (5 pages), rasterizes each at 300dpi (379KB–563KB per page), re-merges to 30MB PDF.
- [x] `examples/trace_logo.py` — round-trip `svglogo.svg` → PNG (130KB) → traced SVG (51KB).
- [x] `examples/layer_stack.py` — stacks `initial.svg`, `hello_glyphs.svg`, `svglogo.svg` into layered SVG (181KB) and layered PDF with 3 OCGs: `['Initial', 'Glyphs', 'Logo']`.
- [x] `examples/regularize_batch.py` — regularizes every fixture; shows real canonicalization effects (e.g. `initial.svg` 174KB → 21KB, `textboard.svg` 9.7MB → 4.7MB, `regularity.pdf` 18MB → 14MB).
- [x] `README.md` — 92 lines, install + Python API example + CLI example + backend table + rejected-backend paragraph.
- [x] `CHANGELOG.md` — Phase 1-8 entry prepended with full accomplishment list.
- [x] `DEPENDENCIES.md` — runtime table with rationale for every dep and rejection list pointing at SPEC.md §2.
- [x] `WORK.md` — all phases marked complete.
- [x] Full test suite: **208 passed, 1 skipped in 20.26s** (skip is pre-existing pdfium test needing a ≥2-page PDF).

## Gate checks (after every phase)

- [ ] `uvx hatch test` green.
- [ ] `uvx ruff check src tests` clean (after `--fix --unsafe-fixes`).
- [ ] `uvx ruff format --check src tests` clean.
- [ ] `uvx mypy src/vexy_pdfsvgpy/` — no new errors.
- [ ] Zero imports from forbidden list: `grep -rE "cairosvg|pdf2image|svglib|reportlab|skia_python|pdfkit|weasyprint" src/` returns nothing.
- [ ] `WORK.md` updated.
- [ ] At least one real-data invocation against `testdata/` documented in `WORK.md`.
