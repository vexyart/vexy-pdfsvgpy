# this_file: src/vexy_pdfsvgpy/__init__.py
"""vexy_pdfsvgpy — unified PDF/SVG/PNG conversion."""
from __future__ import annotations

from pathlib import Path
from typing import Any

try:
    from ._version import version as __version__  # type: ignore[import-not-found]
except ImportError:
    __version__ = "0.0.0+unknown"

from .dispatch import Capability
from .document import Document, Page
from .errors import (
    BackendFailure,
    InvalidInput,
    UnsupportedConversion,
    UnsupportedOnPlatform,
    VexyError,
)
from .pipeline import Step, execute, plan
from .types import Content, FormatSpec, Hint, Hints, Packaging


def convert(
    input: str | Path | None = None,
    output: str | Path | None = None,
    *,
    hints: str | Hints | None = None,
    **options: Any,
) -> Path:
    """High-level conversion entry point.

    Resolves FormatSpecs from file extensions, plans the pipeline, and
    executes it. Returns the output path.
    """
    if input is None or output is None:
        raise InvalidInput("convert() requires both 'input' and 'output'")
    src = Path(input)
    dst = Path(output)
    if not src.exists():
        raise InvalidInput(f"input does not exist: {src}")
    input_spec = FormatSpec.from_extension(src)
    output_spec = FormatSpec.from_extension(dst)
    resolved_hints = Hints.parse(hints) if not isinstance(hints, Hints) else hints
    steps = plan(input_spec, output_spec, resolved_hints, options=options)
    return execute(steps, src, dst)


__all__ = [
    "BackendFailure",
    "Capability",
    "Content",
    "Document",
    "FormatSpec",
    "Hint",
    "Hints",
    "InvalidInput",
    "Packaging",
    "Page",
    "Step",
    "UnsupportedConversion",
    "UnsupportedOnPlatform",
    "VexyError",
    "__version__",
    "convert",
    "execute",
    "plan",
]
