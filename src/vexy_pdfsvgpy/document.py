from __future__ import annotations
# this_file: src/vexy_pdfsvgpy/document.py
"""Document and Page intermediate types for the conversion pipeline."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

from .errors import InvalidInput
from .types import FormatSpec

PageKind = Literal["pdf", "svg", "png", "jpg"]


@dataclass(slots=True)
class Page:
    """One page of content in memory. Kind determines how `content` is read.

    content: bytes for pdf/png/jpg; str for svg (matches get_svg_image() return).
    width/height: PDF user-space points (1/72 inch) for vector; pixels for bitmap.
    dpi: only meaningful for bitmaps.
    label: optional layer name or page title.
    """

    content: bytes | str
    kind: PageKind
    width: float
    height: float
    dpi: float | None = None
    label: str | None = None


@dataclass(slots=True)
class Document:
    """An ordered collection of pages, with an optional source path and spec.

    Passive container — backends do all reading and writing.
    """

    pages: list[Page] = field(default_factory=list)
    source: Path | None = None
    spec: FormatSpec | None = None

    def __len__(self) -> int:
        return len(self.pages)

    def __bool__(self) -> bool:
        return bool(self.pages)

    @property
    def page_count(self) -> int:
        return len(self.pages)

    @property
    def kind(self) -> PageKind | None:
        """Kind of the first page, or None if empty."""
        return self.pages[0].kind if self.pages else None

    def add(self, page: Page) -> None:
        self.pages.append(page)

    @classmethod
    def empty(cls, spec: FormatSpec | None = None) -> Document:
        return cls(pages=[], source=None, spec=spec)

    @classmethod
    def from_path(cls, path: str | Path, *, spec: FormatSpec | None = None) -> Document:
        """Construct a Document referencing an on-disk file.

        Does NOT read or decode the file body; backends do that when needed.
        A single placeholder Page with zero dimensions is inserted so callers
        can inspect ``kind`` without opening the file.  Actual page enumeration
        happens lazily when a backend opens ``source``.

        Raises :exc:`InvalidInput` if the path does not exist or has an
        unrecognised extension (when *spec* is not provided).
        """
        p = Path(path)
        if not p.exists():
            raise InvalidInput(f"source file does not exist: {p}")
        resolved_spec = spec or FormatSpec.from_extension(p)
        placeholder = Page(
            content=b"",
            kind=resolved_spec.format,  # type: ignore[arg-type]
            width=0.0,
            height=0.0,
        )
        return cls(pages=[placeholder], source=p, spec=resolved_spec)
