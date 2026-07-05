---
this_file: CHANGELOG.md
---

# Changelog

## Modernization pass (2026-07-05)

- **CI/CD:** added `.github/workflows/ci.yml` (uv-based lint + strict mypy + pytest matrix on Ubuntu/macOS, Python 3.12/3.13, coverage) and `release.yml` (build + PyPI trusted publishing on `v*` tags).
- **Tests are now self-contained:** added committed `tests/fixtures/` (tiny synthetic PDFs + small SVGs) and a `_generate.py` regenerator; repointed all test data references off the gitignored `testdata/`. The suite runs anywhere, including CI.
- **Coverage:** added in-process CLI unit tests (`tests/test_cli_unit.py`); coverage rose to ~82% (219 tests).
- **Lint/types:** ruff clean and strict mypy clean across `src/` and `tests/`; added per-module mypy overrides for untyped backends, `lxml-stubs`, and per-file ruff ignores for lazy test imports. Normalized module headers (docstring → `this_file` → `from __future__`). Added type hints and comments per the style guide.
- **Packaging:** added `readme`, `keywords`, and trove classifiers to `pyproject.toml`; consolidated the dev toolchain into a PEP 735 `[dependency-groups]` dev group.
- **Docs:** new Jekyll + Just-the-Docs site under `docs/` (backends, format grammar, CLI reference); README badges and project icon (`docs/assets/icon.png`).

## Phase 1-8 — Initial implementation (2026-04-14)

- Bootstrap (`pyproject.toml`, package skeleton, smoke test).
- Format grammar (`FormatSpec`, `Packaging`, `Content`, `Hint`, `Hints`) with round-trip parser.
- Errors (`VexyError` hierarchy) and intermediate types (`Document`, `Page`).
- Path helpers with filename templating.
- Backends: `pymupdf`, `pypdfium2`, `resvg-py`, `pypdf`, `pikepdf`, `vtracer`, `apple` (macOS PDFKit/Quartz), and `wrap` (base64 `<image>`).
- Dispatcher and pipeline planner with per-op backend resolution and hint priority.
- Public `convert()` entry point.
- Reshape operations: `pages2docs`, `docs2pages`, `docs2layers_pdf` (OCGs), `docs2layers_svg` (Inkscape layers).
- Regularize (canonicalization), size-and-crop, and color operations (`gray`, `invert`, `vivid`, `bright`, `contrast`, `backdrop`).
- Fire CLI (`vexy-pdfsvgpy convert|regularize|split|merge`).
- Examples: `convert_coupon.py`, `trace_logo.py`, `layer_stack.py`, `regularize_batch.py`.
- Tests: >100 passing across phases, all hitting real backends and `testdata/` fixtures.

## Unreleased — Phase 0 (Bootstrap)

- Initialized package layout: `src/vexy_pdfsvgpy/`, `tests/`
- Added `pyproject.toml` with hatchling + hatch-vcs build system
- Added smoke test (`tests/test_smoke.py`) that verifies `__version__` is a non-empty string
- Added stub CLI entry point (`cli.py`) — full implementation in Phase 7
- Added `py.typed` marker for PEP 561 compliance
- Added `test.sh` post-edit chain script
