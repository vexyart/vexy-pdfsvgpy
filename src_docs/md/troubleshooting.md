# Troubleshooting

This page lists the errors you are most likely to see, what causes them, and what to do. Error messages are quoted as the CLI prints them.

## Known limitations in the current release

| Limitation | Effect | Workaround |
|---|---|---|
| Transform flags are not wired up | `--gray`, `--invert`, `--vivid`, `--bright`, `--contrast`, `--backdrop`, `--dim`, `--scale`, `--top`, `--bottom`, `--left`, `--right`, `--crop` and `--regularize` fail in cross-format conversions | Convert first, then post-process with another tool. Use `regularize` only for PDF→PDF or SVG→SVG. |
| Only the first page is converted | PDF→PNG and PDF→SVG write page 1 | Pass `page=N` from Python (zero-based), or `split` the PDF first and convert each page |
| No multi-input composition in `convert()` | Several inputs with output packaging `m` or `l` raise `NotImplementedError` | Use `merge`, or `vexy_pdfsvgpy.operations.reshape.docs2layers_pdf` / `docs2layers_svg` |
| No JPG output | Any conversion to `.jpg` raises `UnsupportedConversion` | Write PNG and convert it with Pillow |
| Content qualifier has no effect | `pdf_mt` behaves like `pdf_mo` | Use `text_as="paths"` for outlines |
| Output templates are not applied | `{page:02d}` in `--output` is not expanded | Name the output file yourself |

## Error messages

### `Error: --input and --output are required`

Exit code `2`. Every `convert` call, and every format shortcut, needs both flags.

### `InvalidInput: Cannot infer format from extension '.tif'; ...`

The format comes from the extension, and only `.pdf`, `.svg`, `.png`, `.jpg` and `.jpeg` are known. Rename the file or give an explicit spec with `--vinput`/`--voutput`.

### `InvalidInput: Must specify explicit format specifier (e.g. --binput png_d) for directories`

A directory input has no extension. Add `--vinput pdf_d` (or `svg_d`, `png_d`, `jpg_d`) to say which files to collect.

### `InvalidInput: No matching files found in ...`

The directory has no files with the extension of the input format. Check the format, or add `--recursive` if the files are in subfolders.

### `InvalidInput: Unknown hint 'xx'; expected one of [...]`

Valid hint codes are `ap`, `ca`, `gs`, `mu`, `pk` and `re`.

### `UnsupportedConversion: identity conversion png → png is not supported`

Same-format conversion exists only for PDF and SVG (normalization).

### `UnsupportedConversion: no direct path pdf → jpg`

The planner supports only the pairs listed in [Architecture](architecture.md#planning).

### `BackendFailure: [resvg] svg_to_png failed: svg_to_png() got an unexpected keyword argument 'dpi'`

An option was passed to a backend that does not accept it. `resvg` takes `width`; `pymupdf` takes `dpi`. Either change the option or select the other backend with a hint:

```bash
vexy-pdfsvgpy convert --input logo.svg --output logo.png --hint mu
```

From Python, `convert(..., hints="mu", dpi=96)`.

### `BackendFailure: ... No module named 'ghostscript'` or `'cairosvg'`

The `gs` or `ca` hint was used without the extra. Install it:

```bash
pip install "vexy-pdfsvgpy[ghostscript]"   # or [cairo]
```

These extras also need the Ghostscript or Cairo system library.

### `BackendFailure: [apple] ... unsupported on linux`

The `ap` hint works only on macOS. Remove it on other platforms. A fallback such as `--hint ap,mu` does not help: the dispatcher picks the backend before it runs, so `ap,mu` selects Apple on every platform.

## Output looks wrong

### Text in the SVG uses the wrong font

By default PDF→SVG keeps text as `<text>` elements that refer to fonts by name. A viewer without those fonts substitutes others. Use `--text_as paths` to draw glyphs as outlines.

### The PNG from an SVG has an unexpected size

`resvg` renders at 2048 pixels wide by default, whatever the SVG's own size. Pass `width=` from Python, or use `--hint mu` to render at 300 dpi relative to the SVG's size.

### The PNG from a PDF is very large

`pymupdf` renders at 300 dpi. From Python, pass a lower `dpi`, for example `dpi=96`.

## Get debug output

`--verbose` sets the log level to `DEBUG`, but in the current release the CLI sends log messages to a sink that discards them, so the flag adds no output. For a full Python traceback, call the API directly:

```bash
python -c "from vexy_pdfsvgpy import convert; convert(input='in.pdf', output='out.png')"
```

## Report a problem

Open an issue at <https://github.com/vexyart/vexy-pdfsvgpy/issues> with the command, the full error, the output of `vexy-pdfsvgpy version`, your Python version and your operating system.
