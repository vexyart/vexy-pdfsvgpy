# Contributing

## Set up a development environment

Prerequisites: Python 3.12 or later, [`uv`](https://docs.astral.sh/uv/) and git.

1. Clone the repository:

    ```bash
    git clone https://github.com/vexyart/vexy-pdfsvgpy.git
    cd vexy-pdfsvgpy
    ```

2. Install the package and the `dev` dependency group (`pytest`, `pytest-cov`, `ruff`, `mypy`, `lxml-stubs`):

    ```bash
    uv sync --dev
    ```

## Run the checks

These are the commands CI runs (`.github/workflows/ci.yml`):

```bash
uv run ruff check src tests
uv run ruff format --check src tests
uv run mypy src/vexy_pdfsvgpy
uv run pytest -q
```

`mypy` runs in strict mode. Backends without type information (`vtracer`, `pypdfium2`, `ghostscript`, `cairosvg`, `resvg_py`, `fire`, `Foundation`, `Quartz`) are listed in `[[tool.mypy.overrides]]` in `pyproject.toml`.

CI runs the tests on Ubuntu and macOS with Python 3.12 and 3.13.

`./test.sh` runs the maintainer's full post-edit chain: `autoflake`, `pyupgrade`, `ruff check --fix`, `ruff format` and `uvx hatch test`. It needs `fd`.

## Test fixtures

Tests read small committed files from `tests/fixtures/`: three synthetic PDFs (`fontlab_posters.pdf`, `papercut.pdf`, `regularity.pdf`) and SVGs (`hello_glyphs.svg`, `initial.svg`, `tiger.svg`). Regenerate the PDFs with:

```bash
uv run python tests/fixtures/_generate.py
```

The larger real-world samples in `testdata/` are not in git and are not needed to run the tests. The scripts in `examples/` read from `testdata/`.

## Examples

`examples/` holds runnable scripts that use the public API:

| Script | What it does |
|---|---|
| `convert_coupon.py` | Splits a PDF, rasterizes each page at 300 dpi, merges the results |
| `trace_logo.py` | SVG → PNG → traced SVG round trip through `vtracer` |
| `layer_stack.py` | Stacks SVGs into a layered SVG and a layered PDF with OCGs |
| `regularize_batch.py` | Normalizes every fixture in `testdata/` |

Run one with `uv run examples/trace_logo.py`.

## Add or change a backend

1. Read `IDEA.md` and `SPEC.md` §2 first. A default backend must install as a self-contained wheel with no system library.
2. Add a module under `src/vexy_pdfsvgpy/backends/`. Functions take `src: Path, dst: Path` plus keyword-only options, return `dst`, and raise `RuntimeError("[name] op failed: ...")`.
3. Register the functions in `dispatch._load_table()` inside `try`/`except ImportError`, with a `Hint`.
4. Add tests under `tests/backends/`.

## Documentation

The documentation source is in `src_docs/md/`, and the site configuration is `src_docs/mkdocs.yml`. [ProperDocs](https://pypi.org/project/properdocs/) with the MaterialX theme builds it into `docs/`, which GitHub Pages serves at <https://vexy.dev/vexy-pdfsvgpy/>.

```bash
src_docs/build.sh          # strict build into docs/
src_docs/build.sh serve    # live preview on http://127.0.0.1:8000
```

The `Docs` workflow rebuilds `docs/` on every push to `main` that changes `src_docs/`. Do not edit `docs/` by hand.

## Build the package

```bash
./build.sh package   # uv build + twine check into dist/
./build.sh docs      # documentation only
./build.sh           # both
```

The version comes from the git tag through `hatch-vcs`. The build writes it into `src/vexy_pdfsvgpy/_version.py`, which is not tracked.

## Release

Releases are tagged `vX.Y.Z`. Two paths publish to PyPI:

- `./publish.sh` runs `gitnextver`, which commits pending changes, tags the next version and pushes. It then builds from the tag and uploads with `uv publish`. It needs a PyPI credential such as `UV_PUBLISH_TOKEN`.
- The `Release` workflow (`.github/workflows/release.yml`) runs on every pushed `v*` tag. It builds the sdist and wheel, checks them with `twine`, and uploads with PyPI trusted publishing. It skips files that are already on PyPI, so it does not fail after `publish.sh` has uploaded the same version.

Record changes in `CHANGELOG.md`.
