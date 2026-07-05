# this_file: src/vexy_pdfsvgpy/errors.py
"""Narrow exception hierarchy for vexy_pdfsvgpy."""

from __future__ import annotations


class VexyError(Exception):
    """Base class for all vexy_pdfsvgpy errors."""


class InvalidInput(VexyError):  # noqa: N818 - public API name, kept for compatibility
    """Bad path, bad FormatSpec string, or unreadable file."""


class UnsupportedConversion(VexyError):  # noqa: N818 - public API name, kept for compatibility
    """No backend can handle this conversion graph edge."""


class BackendFailure(VexyError):  # noqa: N818 - public API name, kept for compatibility
    """A backend raised an exception; wrapped with context."""

    def __init__(self, backend: str, op: str, original: Exception) -> None:
        self.backend = backend
        self.op = op
        self.original = original
        super().__init__(str(self))

    def __str__(self) -> str:
        return f"[{self.backend}] {self.op} failed: {self.original}"


class UnsupportedOnPlatform(VexyError):  # noqa: N818 - public API name, kept for compatibility
    """Operation requires a platform capability not available here (e.g. `ap` on non-darwin)."""
