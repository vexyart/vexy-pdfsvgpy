# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project state

Greenfield. `src/vexy_pdfsvgpy/`, `tests/`, and `examples/` exist but are empty. No `pyproject.toml`, no `README.md`, no source or tests yet. A `.venv/` already exists with the Tier-1 backends pre-installed (`pymupdf`, `pypdfium2`, `pypdf`, `pikepdf`) — inspect `.venv/lib/python3.12/site-packages/` to read real installed code when verifying behavior.

Key files and dirs:

- `IDEA.md` — long-form research notes; the source of truth for why the backend stack looks the way it does. Read before adding or swapping a dependency.
- `external/pdfsvgpy_demo.py` — **653-line reference implementation** (gitignored) that exercises every conversion path (PDF→PNG, PDF→SVG, SVG→PNG, SVG→PDF, PNG→SVG, split/merge) against `testdata/` with every backend, times each one, and writes results to `out/`. Treat it as the executable spec — the real package is essentially "turn this script into a clean library API."
- `testdata/` — sample PDFs (`fontlab_posters.pdf`, `papercut.pdf`, `regularity.pdf`) and SVGs (`hello_glyphs.svg`, `initial.svg`, `tiger.svg`, `svglogo.svg`, `textboard.svg`). Gitignored. Use these as fixtures.
- `out/` — the demo's output directory. Gitignored. Filenames like `hello_glyphs-via-resvg@2048px.png` or `fontlab_posters-pymupdf→pymupdf.pdf` are self-describing — a quick way to see which backend pipelines actually work on real inputs.
- `external/` — vendored upstream source for backends (`pymupdf`, `pypdfium2`, `pypdf`, `pikepdf`, `resvg-py`, `vtracer`) plus raw C source (`mupdf`) and also-rans/rejects kept for comparison only (`svglib`, `skia-python`, `svg2pdf`, `svgpathtools`, `picosvgx`, `PyMuPDF-Utilities`, `vexy-vsvg`). **Gitignored.** Read-only reference material — never edit, never import from, and don't be tempted to depend on the rejected ones.

Any work on this repo starts by creating `pyproject.toml` and the package layout. Don't assume files exist — check first.

## Scope (one sentence)

A single unified Python API over a small, deterministic set of self-contained backends that covers the full PDF ⇄ SVG ⇄ PNG conversion graph plus PDF split/merge, with zero system-library dependencies.

## Backend selection — this is the whole point

`IDEA.md` spends thousands of words filtering libraries by the strict rule **"pip install → works everywhere, no system libs, no post-install setup"**. The conclusion is a fixed stack. Respect it:

| Capability          | Backend                                      |
| ------------------- | -------------------------------------------- |
| PDF → PNG           | `pymupdf` or `pypdfium2`                     |
| PDF → SVG           | `pymupdf` (`page.get_svg_image()`)           |
| SVG → PNG           | `resvg-py` (preferred) or `pymupdf`          |
| SVG → PDF           | `pymupdf` (open SVG, save as PDF)            |
| PDF split / merge   | `pypdf` (simple), `pikepdf` (lossless)       |
| PNG → SVG           | `vtracer`                                    |

**Do not add** `cairosvg`, `pdf2image`, `svglib`, `Pillow` (for PDF), `skia-python`, or anything requiring Cairo / Poppler / Ghostscript / libcairo. They are explicitly rejected in `IDEA.md` because they break the self-contained install rule. If a task seems to need one of those, stop and re-read the relevant section of `IDEA.md` — there is almost always a Tier-1 alternative.

PDF → SVG is inherently lossy (paths get flattened, groups are lost). Don't promise semantic fidelity in the API — document the tradeoff.

## Expected project layout (when you create it)

Standard `src/`-layout Python package, Python 3.12+, managed with `uv` and `hatch-vcs`:

```
pyproject.toml      # hatch-vcs versioning, deps pinned loose
src/vexy_pdfsvgpy/  # the package
tests/              # pytest
examples/           # runnable scripts doubling as functional tests
```

Per user global rules: every source file gets a `this_file: path/from/repo/root` marker near the top (comment for `.py`, YAML frontmatter for `.md`). Use `uv add` for dependencies, never bare `pip`. CLI scripts use the `#!/usr/bin/env -S uv run -s` + inline `# /// script` header.

## Commands

There is no build/test/lint infrastructure yet. Once `pyproject.toml` exists, the user's global conventions apply:

```bash
# Install / sync
uv venv --python 3.12 --clear && uv sync

# Run the full post-edit chain (format, lint, upgrade, test)
fd -e py -x uvx autoflake -i {} \
  ; fd -e py -x uvx pyupgrade --py312-plus {} \
  ; fd -e py -x uvx ruff check --output-format=github --fix --unsafe-fixes {} \
  ; fd -e py -x uvx ruff format --respect-gitignore --target-version py312 {} \
  ; uvx hatch test

# Single test
uvx hatch test tests/test_foo.py::test_bar -xvs
# or
python -m pytest tests/test_foo.py::test_bar -xvs

# Type check a file
uvx mypy src/vexy_pdfsvgpy/foo.py
```

## Working with `external/`

`external/` is **gitignored** and contains upstream source for the backends. It exists so you can grep real implementations when documentation is ambiguous — e.g. verifying `pymupdf.Page.get_svg_image()` signature, checking `pypdfium2` render scale semantics, or confirming `pikepdf` split behavior. Read it; never modify it; never add it to the package imports.

When verifying backend behavior, prefer reading `external/<lib>/` source (or the installed copy under `.venv/lib/python3.12/site-packages/<lib>/`) over guessing from memory. `IDEA.md` already warns that assumptions about undocumented fields cause silent failures. For "does this pipeline actually work on real files?", run or read `external/pdfsvgpy_demo.py` rather than speculating — it's already wired up against `testdata/`.

## Architectural notes for future work

- **One engine per capability, deterministic selection.** The API should pick a backend per operation based on capability, not user preference flags, unless there's a real fidelity tradeoff worth exposing.
- **Parse, don't validate at the edge.** Convert paths/bytes/streams to typed objects at the API boundary; internal code assumes validity.
- **Errors as data at boundaries.** Narrow exceptions (bad input, backend failure, unsupported conversion); don't leak backend-specific exception types.
- **No enterprise bloat.** This is a utility library, not a platform. No circuit breakers, no metrics, no caching layer, no plugin system, no config framework. See user global rules §12.
