from __future__ import annotations
# this_file: src/vexy_pdfsvgpy/pipeline.py
"""Pipeline planning and execution for format conversions."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .dispatch import BackendFn, Capability, resolve
from .errors import BackendFailure, UnsupportedConversion
from .types import FormatSpec, Hints


@dataclass(frozen=True, slots=True)
class Step:
    capability: Capability
    backend: BackendFn
    kwargs: dict[str, Any] = field(default_factory=dict)


# Direct single-hop conversions: (in_fmt, out_fmt) → Capability
_DIRECT: dict[tuple[str, str], Capability] = {
    ("pdf", "png"): Capability.PDF_TO_PNG,
    ("pdf", "svg"): Capability.PDF_TO_SVG,
    ("svg", "pdf"): Capability.SVG_TO_PDF,
    ("svg", "png"): Capability.SVG_TO_PNG,
    ("png", "svg"): Capability.PNG_TO_SVG_TRACE,
    ("jpg", "svg"): Capability.PNG_TO_SVG_TRACE,
    ("png", "pdf"): Capability.BITMAP_TO_PDF,
    ("jpg", "pdf"): Capability.BITMAP_TO_PDF,
}

# Same-format normalisation
_NORMALIZE: dict[str, Capability] = {
    "pdf": Capability.PDF_NORMALIZE,
    "svg": Capability.SVG_NORMALIZE,
}


def plan(
    input_spec: FormatSpec,
    output_spec: FormatSpec,
    hints: Hints | None = None,
    *,
    options: dict[str, Any] | None = None,
) -> list[Step]:
    """Plan a conversion pipeline from input_spec to output_spec.

    Returns an ordered list of Steps. Pass to execute() to run.
    Raises UnsupportedConversion when no path exists.
    """
    hints = hints or Hints()
    options = options or {}
    in_fmt = input_spec.format
    out_fmt = output_spec.format

    if in_fmt == out_fmt:
        cap = _NORMALIZE.get(in_fmt)
        if cap is None:
            raise UnsupportedConversion(
                f"identity conversion {in_fmt} → {out_fmt} is not supported"
            )
        return [Step(cap, resolve(cap, hints))]

    cap = _DIRECT.get((in_fmt, out_fmt))
    if cap is None:
        raise UnsupportedConversion(f"no direct path {in_fmt} → {out_fmt}")

    return [Step(cap, resolve(cap, hints), kwargs=dict(options))]


def execute(steps: list[Step], src: Path, dst: Path) -> Path:
    """Execute a planned pipeline, writing the result to dst.

    For multi-step pipelines writes intermediate files next to dst.
    Returns dst on success.
    """
    if not steps:
        raise UnsupportedConversion("empty pipeline")

    current = src
    for i, step in enumerate(steps):
        is_last = i == len(steps) - 1
        step_dst = dst if is_last else dst.with_suffix(f".step{i}.tmp")
        try:
            step.backend.func(current, step_dst, **step.kwargs)
        except BackendFailure:
            raise
        except Exception as e:
            raise BackendFailure(step.backend.name, step.capability.value, e) from e
        current = step_dst

    return dst
