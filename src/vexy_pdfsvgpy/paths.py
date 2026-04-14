from __future__ import annotations

# this_file: src/vexy_pdfsvgpy/paths.py

"""File path rendering helpers for vexy-pdfsvgpy output naming."""

import string
from pathlib import Path

class _CheckingMap(dict):
    """A dict subclass that records any key lookup not in the allowed set."""

    def __init__(self, data: dict, *, unknown_keys: list[str]) -> None:
        super().__init__(data)
        self._unknown = unknown_keys

    def __missing__(self, key: str) -> str:
        self._unknown.append(key)
        return f"{{{key}}}"


def render_output(
    template: str | Path,
    *,
    stem: str,
    page: int,
    index: int = 0,
    total_pages: int = 1,
    backend: str = "",
    ext: str,
    scale: str = "",
) -> Path:
    """Render an output file path from *template* by substituting placeholders.

    Placeholders: ``{stem}``, ``{page}``, ``{page:02d}``, ``{index}``,
    ``{backend}``, ``{ext}``, ``{scale}``.

    Auto-pagination: if the template contains no ``{page}`` placeholder and
    *total_pages* > 1, ``-p{page:0Nd}`` is inserted before the final
    extension (N = max(2, len(str(total_pages)))).

    Raises ``ValueError`` for unknown placeholders, empty *stem*, or empty *ext*.
    """
    if not stem:
        raise ValueError("stem must not be empty")
    if not ext:
        raise ValueError("ext must not be empty")

    tmpl_str = str(template)

    # Detect whether {page} or {page:...} appears in the template.
    has_page_placeholder = _has_page_placeholder(tmpl_str)

    # Normalise ext: strip leading dot for the placeholder value.
    ext_value = ext.lstrip(".")

    unknown: list[str] = []
    mapping = _CheckingMap(
        {
            "stem": stem,
            "page": page,
            "index": index,
            "backend": backend,
            "ext": ext_value,
            "scale": scale,
        },
        unknown_keys=unknown,
    )

    try:
        resolved = string.Formatter().vformat(tmpl_str, (), mapping)
    except (KeyError, ValueError) as exc:
        raise ValueError(f"Invalid template '{tmpl_str}': {exc}") from exc

    if unknown:
        raise ValueError(
            f"Unknown placeholder(s) in template '{tmpl_str}': {unknown}"
        )

    result = Path(resolved)

    # Auto-pagination: insert -pNNN before the extension when needed.
    if not has_page_placeholder and total_pages > 1:
        pad = max(2, len(str(total_pages)))
        page_suffix = f"-p{page:0{pad}d}"
        suffix = result.suffix  # e.g. ".png" or ""
        result = result.with_name(result.stem + page_suffix + suffix)

    # If the resolved path has no extension, append .{ext}.
    if not result.suffix:
        result = result.with_name(result.name + "." + ext_value)

    return result


def _has_page_placeholder(template: str) -> bool:
    """Return True if *template* contains a ``{page}`` or ``{page:...}`` field.

    ``string.Formatter.parse`` yields ``(literal, field_name, format_spec,
    conversion)``; field_name for ``{page:02d}`` is simply ``"page"``.
    """
    for _, field_name, _, _ in string.Formatter().parse(template):
        if field_name == "page":
            return True
    return False


def parse_scale_suffix(width: int | None, dpi: int | None) -> str:
    """Return '@{width}px', '@{dpi}dpi', or '' for the filename scale suffix."""
    if width is not None:
        return f"@{width}px"
    if dpi is not None:
        return f"@{dpi}dpi"
    return ""


def ensure_parent(path: Path) -> Path:
    """Create the parent directory of *path* if it does not exist, then return *path*."""
    path.parent.mkdir(parents=True, exist_ok=True)
    return path
