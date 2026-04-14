from __future__ import annotations
# this_file: src/vexy_pdfsvgpy/operations/reshape.py
"""Reshape operations: pages ↔ documents, layers ↔ documents."""

import copy
from pathlib import Path

NS_SVG = "http://www.w3.org/2000/svg"
NS_INKSCAPE = "http://www.inkscape.org/namespaces/inkscape"
_LAYER_ATTR = f"{{{NS_INKSCAPE}}}groupmode"
_LABEL_ATTR = f"{{{NS_INKSCAPE}}}label"


def pages2docs_pdf(src: Path, out_dir: Path, *, stem: str | None = None) -> list[Path]:
    """Split a multi-page PDF into one-page PDFs. Delegates to pikepdf for lossless.

    Filename convention: {stem}-page-{i+1:0{pad}d}.pdf
    """
    from ..backends import pikepdf_backend
    return pikepdf_backend.split(src, out_dir, stem=stem)


def docs2pages_pdf(srcs: list[Path], dst: Path) -> Path:
    """Merge single-page (or multi-page) PDFs into one multi-page PDF. Lossless via pikepdf."""
    from ..backends import pikepdf_backend
    return pikepdf_backend.merge(srcs, dst)


def docs2layers_pdf(srcs: list[Path], dst: Path, *, labels: list[str] | None = None) -> Path:
    """Stack multiple PDFs as OCGs (optional content groups) on a single page.

    Creates one output page whose mediabox matches the first source. Each source PDF's
    first page is drawn into its own named OCG via `page.show_pdf_page(rect, src, 0, oc=ocg)`.
    Toggleable in Acrobat / Apple Preview.

    `labels` — optional list of layer names; defaults to `Layer 1`, `Layer 2`, etc.
    """
    try:
        import pymupdf
        out = pymupdf.open()
        src_docs = [pymupdf.open(str(s)) for s in srcs]
        try:
            first = src_docs[0]
            rect = first[0].rect
            page = out.new_page(width=rect.width, height=rect.height)
            effective_labels = labels or [f"Layer {i + 1}" for i in range(len(srcs))]
            for src_doc, label in zip(src_docs, effective_labels, strict=False):
                ocg_xref = out.add_ocg(label, on=True)
                page.show_pdf_page(page.rect, src_doc, 0, oc=ocg_xref)
            dst.parent.mkdir(parents=True, exist_ok=True)
            out.save(str(dst), garbage=4, deflate=True)
            return dst
        finally:
            for s in src_docs:
                s.close()
            out.close()
    except Exception as e:
        raise RuntimeError(f"[reshape] docs2layers_pdf failed: {e}") from e


def docs2layers_svg(srcs: list[Path], dst: Path, *, labels: list[str] | None = None) -> Path:
    """Stack multiple SVGs as named Inkscape layers in a single SVG.

    Parses each source with lxml, wraps each root's children in a
    <g inkscape:groupmode="layer" inkscape:label="..."> group, and composes
    them into one output SVG. The viewBox and width/height are taken from
    the first source.
    """
    try:
        from lxml import etree
        roots = [etree.parse(str(s)).getroot() for s in srcs]
        first = roots[0]
        width = first.get("width", "800")
        height = first.get("height", "600")
        viewbox = first.get("viewBox", f"0 0 {width} {height}")

        nsmap = {None: NS_SVG, "inkscape": NS_INKSCAPE}
        out = etree.Element(f"{{{NS_SVG}}}svg", nsmap=nsmap)
        out.set("width", width)
        out.set("height", height)
        out.set("viewBox", viewbox)

        effective_labels = labels or [f"Layer {i + 1}" for i in range(len(srcs))]
        for i, (root, label) in enumerate(zip(roots, effective_labels, strict=False)):
            g = etree.SubElement(out, f"{{{NS_SVG}}}g")
            g.set("id", f"layer{i + 1}")
            g.set(_LAYER_ATTR, "layer")
            g.set(_LABEL_ATTR, label)
            for child in root:
                g.append(copy.deepcopy(child))

        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_bytes(etree.tostring(out, xml_declaration=True, encoding="utf-8", pretty_print=True))
        return dst
    except RuntimeError:
        raise
    except Exception as e:
        raise RuntimeError(f"[reshape] docs2layers_svg failed: {e}") from e


def layers2docs_svg(src: Path, out_dir: Path) -> list[Path]:
    """Split a layered SVG into one document per <g> group that has
    inkscape:groupmode="layer". Returns the list of output paths. Each
    output SVG preserves the source's width/height/viewBox and contains
    only the children of one layer group.
    """
    try:
        from lxml import etree
        tree = etree.parse(str(src))
        root = tree.getroot()

        width = root.get("width", "800")
        height = root.get("height", "600")
        viewbox = root.get("viewBox", f"0 0 {width} {height}")

        layers = [el for el in root if el.get(_LAYER_ATTR) == "layer"]
        if not layers:
            layers = [el for el in root if el.tag == f"{{{NS_SVG}}}g"]

        out_dir.mkdir(parents=True, exist_ok=True)
        outputs: list[Path] = []

        nsmap = {None: NS_SVG, "inkscape": NS_INKSCAPE}
        for i, layer in enumerate(layers):
            label = layer.get(_LABEL_ATTR) or layer.get("id") or str(i + 1)
            safe_label = label.replace(" ", "_").replace("/", "-")
            out_svg = etree.Element(f"{{{NS_SVG}}}svg", nsmap=nsmap)
            out_svg.set("width", width)
            out_svg.set("height", height)
            out_svg.set("viewBox", viewbox)
            for child in layer:
                out_svg.append(copy.deepcopy(child))
            dst = out_dir / f"{src.stem}-{safe_label}.svg"
            dst.write_bytes(etree.tostring(out_svg, xml_declaration=True, encoding="utf-8", pretty_print=True))
            outputs.append(dst)

        return outputs
    except RuntimeError:
        raise
    except Exception as e:
        raise RuntimeError(f"[reshape] layers2docs_svg failed: {e}") from e
