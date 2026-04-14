# this_file: tests/test_smoke.py
"""Bootstrap smoke test."""
from __future__ import annotations

import vexy_pdfsvgpy


def test_package_imports() -> None:
    assert isinstance(vexy_pdfsvgpy.__version__, str)
    assert vexy_pdfsvgpy.__version__
