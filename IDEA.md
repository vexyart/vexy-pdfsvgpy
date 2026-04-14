# pdfsvgpy

`pdfsvgpy` should be a Python package and a Fire CLI tool. 

## Tool stack 

### PDF 

#### Apple frameworks

- see external/pdfsvgpy_demo.py and external/fl-uap-2604-coupon.command

#### PikePDF 

- PyPI https://pypi.org/project/pikepdf/ 
- Github https://github.com/pikepdf/pikepdf
- Local copy external/pikepdf

#### PyMuPDF 

- PyPI https://pypi.org/project/PyMuPDF/ 
- Github https://github.com/pymupdf/pymupdf 
- Local copy external/pymupdf

### SVG 

#### ReSVG / usvg

- PyPI https://pypi.org/project/resvg_py/ 
- Github https://github.com/baseplate-admin/resvg-py 
- Github https://github.com/typst/svg2pdf (doesn’t build)
- Github https://github.com/linebender/resvg 
- Local copy external/resvg-py
- Local copy external/svg2pdf
- Local copy external/resvg

#### Svgelements 

- PyPI https://pypi.org/project/svgelements/ 
- Github https://github.com/deeplook/svgelements
- Local copy external/svgelements

#### svgpathtools

- PyPI https://pypi.org/project/svgpathtools/ 
- Github https://github.com/mathandy/svgpathtools
- Local copy external/svgpathtools

#### picosvgx 

- PyPI https://pypi.org/project/picosvgx/ 
- Github https://github.com/ximinng/picosvgx
- Local copy external/picosvgx

#### vexy-vsvg 

- PyPI None (Rust only)
- Github https://github.com/vexyart/vexy-vsvg
- Local copy external/vexy-vsvg

## General notes 

Storing embedded fonts inside SVG is not reliable. SVG fonts are deprecated and many tools don’t handle `glyph` objects embedded inside SVG at all.  


## Input and output file format support

The tool should support the following input and output file formats. It should choose an optimal path of tools to be used during the transformation, depending on the input format, the output format, and the operations to be performed. It should accept 'hints' from the user to use certain tools if multiple tools are available for the same transformation or operation. 

There are two types of formats: vector and bitmap. 

There are four roles of format: --vinput, --voutput, --binput, --boutput. There is also the simplified specification: --input, --output, which can take for either vector or bitmap. 

If --binput is specified, a vinput can be specified or is implied, and the tool will package the input bitmap into a vector input format for further processing. If --input is a bitmap, then it’s used as --binput
If --boutput is specified, a voutput can be specified or is implied, and the tool will first route the data to the voutput format and then rasterize into the boutput format. If --output is a bitmap, then it’s used as --boutput
If --vinput is specified, then we don’t deal with input bitmaps so we skip the packaging step. If --input is a vector, then it’s used as --vinput
If --voutput is specified, then we don’t deal with output bitmaps so we skip the rasterization step. If --output is a vector, then it’s used as --voutput

### Vector format: `pdf`

Packaging qualifiers: 

- `d` for collection of single-page files (DEFAULT, can be omitted)
- `m` for multi-page file
- `l` for layered single-page file
- `s` for single-page file

Content qualifiers: 

- `o` for outlines (DEFAULT)
- `t` for text, with embedded fonts if possible
- `b` for bitmap-only 

The fully qualified format names is `{format}-{packaging}{content}`, for example `pdf-mo` means a multi-page PDF file with outlines. Either the packaging or the content qualifiers can be omitted for output if they are the default.

### Vector format: `svg`

Packaging qualifiers: 

- `d` for collection of files (DEFAULT, can be omitted)
- `l` for layered single-page file
- `s` for single-page file

Content qualifiers: 

- `o` for outlines (DEFAULT)
- `t` for text, with embedded fonts if possible
- `b` for bitmap-only 

### Bitmap format: `png`

Packaging qualifiers: 

- `d` for collection of files (DEFAULT, can be omitted)
- `l` for layered single-page file (= APNG with multiple frames and 0 delay between the frames)

### Bitmap format: `jpg`

Packaging qualifiers: 

- `d` for collection of files (DEFAULT, can be omitted)

## Tool hints

- `re`: prefer resvg_py / usvg (implies SVG being involved)
- `mu`: prefer PyMuPDF (implies PDF being involved)
- `pk`: prefer PikePDF (implies PDF being involved)
- `ap`: prefer Apple frameworks on macOS for PDF

## Documents, pages and layers

If vinput is `m` (PDF only), then each page is treated as a document, so we need to separate the pages into documents (pages2docs). 
If vinput is `l`, then each layer is treated as a document, so we need to separate the layers into documents (layers2docs). 
If vinput is `d`, then each file is treated as a document. If vinput is `s`, then it’s like `d` with just a single file. 

If voutput is `m` (PDF only), then each document becomes a page (docs2pages).
If voutput is `l`, then each document becomes a layer (docs2layers). 
If voutput is `d`, then each document becomes a file. If voutput is `s`, then it’s like `d` with just a single file. 

## Pages and layers to documents on input 

- pages2docs, PDF input: 
  - pk: `pdf.pages.extend(source.pages[:n])`
  - mu: `doc.insert_pdf(doc, from_page=i, to_page=i)`
- docs2pages, PDF output: 
  - pk: `pdf.pages.extend(source.pages)`
  - mu: `doc.insert_pdf(doc)`
- layers2docs, PDF input: mu: convert_to_pdf after using set_layer_ui_config to set the layer UI config
- layers2docs, SVG input: Use an SVG parser to somehow split SVG groups into documents 
- layers2docs, PNG output: If input is an APNG, then each frame is treated as a document

## Documents to pages and layers on output 

### docs2pages, PDF output

Use pk or mu

### docs2layers, PDF output

use mu

### docs2layers

This assumes that all documents have the same width x height dimensions, if not, we need to perform the size-and-crop operation first to harmonize them

#### PDF output, mu hint

This is the most powerful approach if your target is a **PDF with proper toggleable layers**. PyMuPDF has full support for Optional Content Groups (OCGs) — the PDF spec's native layer mechanism. [pymupdf.readthedocs](https://pymupdf.readthedocs.io/en/latest/recipes-optional-content.html)

The workflow:
1. Open each source PDF or page
2. Create a new output PDF with one target page
3. For each source, create an OCG (layer) via `doc.add_ocg(name, on=True)`
4. Use `page.show_pdf_page(rect, src_doc, page_num, oc=ocg_xref)` to draw each source page onto the target page, bound to its OCG

```python
import pymupdf

sources = ["layer1.pdf", "layer2.pdf", "layer3.pdf"]
out = pymupdf.open()
page = out.new_page(width=595, height=842)

for i, path in enumerate(sources):
    src = pymupdf.open(path)
    ocg_xref = out.add_ocg(f"Layer {i+1}", on=True)
    page.show_pdf_page(page.rect, src, 0, oc=ocg_xref)
    src.close()

out.save("stacked_layers.pdf", garbage=4, deflate=True)
```

The result is a **single PDF page** where each source is assigned to its own named OCG, togglable in Acrobat/Viewer. `get_ocgs()` returns a dict of `{xref: {name, on, intent}}` for introspection. This also works for SVG inputs: render each SVG to a temporary PDF first via `resvg_py` (PNG) then embed, or use PyMuPDF's built-in SVG→PDF open. [github](https://github.com/pymupdf/PyMuPDF/discussions/796)

#### PDF output, pk hint (default)

pikepdf `add_overlay()` with Form XObjects (Best for PDF-in, flat PDF-out)

pikepdf's `Page.add_overlay()` and `Page.add_underlay()` use **Form XObjects** — the PDF mechanism for compositing page content. This is clean, spec-compliant, and preserves annotations and hyperlinks. [pikepdf.readthedocs](https://pikepdf.readthedocs.io/en/latest/topics/overlays.html)

```python
from pikepdf import Pdf, Page, Rectangle

pdfs = [Pdf.open(p) for p in ["a.pdf", "b.pdf", "c.pdf"]]
base = pdfs[0]
dest = Page(base.pages[0])
rect = dest.mediabox  # full-page overlay

for src_pdf in pdfs[1:]:
    src_page = base.copy_foreign(src_pdf.pages[0])
    dest.add_overlay(Page(src_page), Rectangle(*rect))

base.save("stacked_flat.pdf")
```

Each source page is drawn on top of the previous via Form XObjects. The result is a **flat composite** — no toggleable layers, but very robust across PDF viewers. For a layered result, combine this with pikepdf's low-level `/OCProperties` dict manipulation via `pikepdf.Dictionary`. Note that `add_overlay` resets the transformation matrix and wraps existing streams in a `q/Q` push/pop pair by default. [pikepdf.readthedocs](https://pikepdf.readthedocs.io/en/latest/topics/overlays.html)

#### SVG output

`<g>` Group Stacking with lxml + resvg_py (Best for SVG-in, SVG-out)

For SVG-to-SVG layering, build a composite SVG manually using `lxml`, wrapping each source SVG's content in a named `<g id="layer-N">` group — the SVG equivalent of a layer. Then optionally rasterize the result with `resvg_py`. [github](https://github.com/sparkfish/resvg-py)

```python
from lxml import etree
import copy, resvg_py

NS = "http://www.w3.org/2000/svg"
svgs = ["a.svg", "b.svg", "c.svg"]

# Parse first to get canvas dimensions
roots = [etree.parse(f).getroot() for f in svgs]
w = roots[0].get("width", "800")
h = roots[0].get("height", "600")

out_svg = etree.Element("svg", nsmap={None: NS,
    "inkscape": "http://www.inkscape.org/namespaces/inkscape"})
out_svg.set("width", w); out_svg.set("height", h)
out_svg.set("viewBox", f"0 0 {w} {h}")

for i, root in enumerate(roots):
    g = etree.SubElement(out_svg, "g")
    g.set("id", f"layer{i+1}")
    # Inkscape-compatible layer label
    g.set("{http://www.inkscape.org/namespaces/inkscape}label", f"Layer {i+1}")
    g.set("{http://www.inkscape.org/namespaces/inkscape}groupmode", "layer")
    for child in root:
        g.append(copy.deepcopy(child))

svg_str = etree.tostring(out_svg, pretty_print=True).decode()
with open("stacked.svg", "w") as f:
    f.write(svg_str)

# Optionally rasterize with resvg_py
png_bytes = resvg_py.svg_to_bytes(svg_string=svg_str)
with open("stacked.png", "wb") as f:
    f.write(png_bytes)
```

The `inkscape:groupmode="layer"` and `inkscape:label` attributes cause Inkscape (and compatible tools) to recognize each `<g>` as a named, toggleable layer. `resvg_py` renders the final flattened composite to PNG at any DPI. For PDF input going into SVG, first export each page via `page.get_svg_image()` in PyMuPDF, then pipe through this compositor. [stackoverflow](https://stackoverflow.com/questions/71474396/stack-svg-layers-with-python)

## `--regularize`

- if vinput is an SVG document, pass it through usvg (from resvg)
- if input is a PDF page, pass it through PyMuPDF convert_to_pdf() 

## size-and-crop

size-and-crop harmonizes the visible area of all documents to the target dimensions. In the CLI it’s triggered if `dim` is given and not `none`. 

### Dimensions 

#### Parameter `--dim` = target dimension, with values: 

- `none` (default) = don’t change the dimension, don’t perform the size-and-crop operation
- `largest` = largest document, 
- `first` = first document,
- `last` = last document,
- specific `"WWWWxHHHH"` dimension in pixels

If `dim` is given, we also must add a transparent rectangle to the each document that is sized to the target dimension, regardless of the scaling and cropping. 

#### Parameter `--scale` = scaling method, with values: 

- `fit` (default)
- `keep`
- `NNN` (%)
- `width` (fit to dim width, adapt the height)
- `height` (fit to dim height, adapt the width)

#### Alignment parameters `--top`, `--bottom`, `--left`, `--right`

- `--top` with value: `NNN` (%) or `auto` (default), 
- `--bottom` with value: `NNN` (%) or `auto` (default), 
- `--left` with value: `NNN` (%) or `auto` (default), 
- `--right` with value: `NNN` (%) or `auto` (default)

This works like CSS; if top and botom margins are specified, bottom is auto; if left and right margins are specified, right is auto; 

#### Parameter `--crop`

Crop and pad to the target dimension after scaling. Possible values: 

- `all` (default) = crop and pad with transparency to the precise target dimension
- `keep` = don’t crop or pad
- `width` = only crop to the target width those that are wider
- `height` = only crop to the target height those that are taller
- `down` = only crop to the target width those that are wider and crop to the target height those that are taller

## Color 

- Parameter `--gray`: if given, convert to grayscale

- Parameter `--invert`: if given, invert the color

- Parameter `--vivid N`: if given, increase the vividness / saturation of colors by N

- Parameter `--bright`: if given, increase the brightness of colors by N or decrease if N < 0

- Parameter `--contrast N`: if given, increase the contrast of colors by N or decrease if N < 0

- Parameter `--backdrop COLOR`: if given, add a backdrop color (rectangle filled with that color) to every page, where color can be `#rrggbb` or `rrggbbaa` or `white` or `black` or `dominant` If it’s `dominant`, we rasterize the page and use the dominant color of the bitmap. 

