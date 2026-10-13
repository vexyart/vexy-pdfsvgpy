# Installation

## Requirements

- Python 3.12 or later.
- A platform with wheels for the dependencies. CI tests Ubuntu and macOS. The Apple Quartz backend (hint `ap`) works only on macOS.

## Install the package

=== "uv"

    ```bash
    uv add vexy-pdfsvgpy
    ```

=== "pip"

    ```bash
    pip install vexy-pdfsvgpy
    ```

=== "uv tool (CLI only)"

    ```bash
    uv tool install vexy-pdfsvgpy
    ```

The install pulls these runtime dependencies:

| Package | Role |
|---|---|
| `pymupdf` | PDF to PNG, PDF to SVG, SVG to PDF, normalization |
| `pypdfium2` | Alternate PDF to PNG renderer |
| `pypdf` | Pure-Python PDF split and merge |
| `pikepdf` | Lossless PDF split and merge |
| `resvg-py` | SVG to PNG through the Rust `resvg` renderer |
| `vtracer` | PNG or JPG to SVG tracing |
| `Pillow` | Bitmap metadata and color operations |
| `lxml` | Layered SVG composition and splitting |
| `fire`, `loguru`, `rich` | CLI, logging, terminal output |
| `pyobjc-framework-Quartz`, `pyobjc-framework-Cocoa` | macOS only: the `ap` backend |

## Optional extras

Two backends sit behind extras because they need system libraries, which the core package avoids.

```bash
pip install "vexy-pdfsvgpy[cairo]"        # CairoSVG, used by hint "ca"
pip install "vexy-pdfsvgpy[ghostscript]"  # Ghostscript bindings, used by hint "gs"
pip install "vexy-pdfsvgpy[all]"          # both
```

The `cairo` extra needs the Cairo library on the system. The `ghostscript` extra needs a Ghostscript installation. Without them, the `ca` and `gs` hints fail when the conversion runs.

## Check the install

1. Print the version:

    ```bash
    vexy-pdfsvgpy version
    ```

    The command prints the installed version.

2. Check the import from Python:

    ```bash
    python -c "import vexy_pdfsvgpy; print(vexy_pdfsvgpy.__version__)"
    ```

You can also run the package as a module: `python -m vexy_pdfsvgpy version`.

## Install from source

1. Clone the repository:

    ```bash
    git clone https://github.com/vexyart/vexy-pdfsvgpy.git
    cd vexy-pdfsvgpy
    ```

2. Create the environment with the development tools:

    ```bash
    uv sync --dev
    ```

3. Run the CLI from the checkout:

    ```bash
    uv run vexy-pdfsvgpy version
    ```

The version comes from the latest git tag through `hatch-vcs`, so a checkout between releases reports a development version such as `0.0.6.dev2+g996b83d04`.
