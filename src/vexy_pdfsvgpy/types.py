# this_file: src/vexy_pdfsvgpy/types.py
"""Format grammar types: FormatSpec, Packaging, Content, Hint, Hints."""
from __future__ import annotations

from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from typing import Literal

from .errors import InvalidInput

# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

VectorFormat = Literal["pdf", "svg"]
BitmapFormat = Literal["png", "jpg"]
Format = Literal["pdf", "svg", "png", "jpg"]

VECTOR_FORMATS: frozenset[str] = frozenset({"pdf", "svg"})
BITMAP_FORMATS: frozenset[str] = frozenset({"png", "jpg"})


class Packaging(StrEnum):
    D = "d"  # collection of single-page files (default)
    M = "m"  # multi-page file (PDF only)
    L = "l"  # layered single-page file
    S = "s"  # single-page file


class Content(StrEnum):
    O = "o"  # outlines / text-as-path (default for vector)
    T = "t"  # text with embedded fonts
    B = "b"  # bitmap-only


class Hint(StrEnum):
    RE = "re"  # prefer resvg
    MU = "mu"  # prefer pymupdf
    PK = "pk"  # prefer pikepdf
    AP = "ap"  # prefer Apple PDFKit / Quartz (macOS only)


# ---------------------------------------------------------------------------
# FormatSpec
# ---------------------------------------------------------------------------

_VALID_FORMATS: frozenset[str] = frozenset({"pdf", "svg", "png", "jpg"})
_VALID_PACKAGING: dict[str, Packaging] = {p.value: p for p in Packaging}
_VALID_CONTENT: dict[str, Content] = {c.value: c for c in Content}


@dataclass(frozen=True, slots=True)
class FormatSpec:
    """Parsed representation of a format qualifier string like ``pdf-mo``."""

    format: Format
    packaging: Packaging = Packaging.D
    content: Content | None = None

    def __post_init__(self) -> None:
        fmt = self.format
        pkg = self.packaging
        cnt = self.content

        # Bitmap formats must not carry a content qualifier.
        if fmt in BITMAP_FORMATS and cnt is not None:
            raise InvalidInput(
                f"Bitmap format {fmt!r} does not support a content qualifier; got {cnt!r}"
            )

        # JPG has no layered form (APNG is png-only).
        if fmt == "jpg" and pkg == Packaging.L:
            raise InvalidInput("jpg does not support layered packaging ('l')")

        # SVG has no multi-page form.
        if fmt == "svg" and pkg == Packaging.M:
            raise InvalidInput("svg does not support multi-page packaging ('m')")

        # For vector formats, default content to Content.O when None.
        if fmt in VECTOR_FORMATS and cnt is None:
            object.__setattr__(self, "content", Content.O)

    # ------------------------------------------------------------------
    # Parsing
    # ------------------------------------------------------------------

    @classmethod
    def parse(cls, s: str) -> FormatSpec:
        """Parse a format qualifier string into a FormatSpec.

        Accepts: ``"pdf"``, ``"pdf-m"``, ``"pdf-mo"``, ``"svg-lt"``,
        ``"png"``, ``"png-l"``, ``"jpg"``, etc.
        Raises :exc:`InvalidInput` on malformed input.
        """
        if not s:
            raise InvalidInput("Empty format spec string")

        parts = s.split("-", 1)
        fmt_str = parts[0].lower()

        if fmt_str not in _VALID_FORMATS:
            raise InvalidInput(
                f"Unknown format {fmt_str!r}; expected one of {sorted(_VALID_FORMATS)}"
            )
        fmt: Format = fmt_str  # type: ignore[assignment]

        if len(parts) == 1:
            # No qualifier — use defaults (validated in __post_init__).
            return cls(format=fmt)

        qualifier = parts[1].lower()
        if not qualifier:
            raise InvalidInput(f"Empty qualifier in {s!r}")

        # First char is packaging.
        pkg_char = qualifier[0]
        if pkg_char not in _VALID_PACKAGING:
            raise InvalidInput(
                f"Unknown packaging qualifier {pkg_char!r} in {s!r}; "
                f"expected one of {sorted(_VALID_PACKAGING)}"
            )
        pkg = _VALID_PACKAGING[pkg_char]

        # Optional second char is content (vector only).
        cnt: Content | None = None
        if len(qualifier) >= 2:
            cnt_char = qualifier[1]
            if fmt in BITMAP_FORMATS:
                raise InvalidInput(
                    f"Bitmap format {fmt!r} does not support a content qualifier; "
                    f"got {cnt_char!r} in {s!r}"
                )
            if cnt_char not in _VALID_CONTENT:
                raise InvalidInput(
                    f"Unknown content qualifier {cnt_char!r} in {s!r}; "
                    f"expected one of {sorted(_VALID_CONTENT)}"
                )
            cnt = _VALID_CONTENT[cnt_char]

        if len(qualifier) > 2:
            raise InvalidInput(f"Qualifier too long in {s!r}; expected at most 2 chars")

        return cls(format=fmt, packaging=pkg, content=cnt)

    @classmethod
    def from_extension(cls, path: str | Path) -> FormatSpec:
        """Infer a default FormatSpec from a file extension.

        Raises :exc:`InvalidInput` on unknown extension.
        """
        suffix = Path(path).suffix.lower()
        mapping: dict[str, str] = {
            ".pdf": "pdf",
            ".svg": "svg",
            ".png": "png",
            ".jpg": "jpg",
            ".jpeg": "jpg",
        }
        if suffix not in mapping:
            raise InvalidInput(
                f"Cannot infer format from extension {suffix!r}; "
                f"expected one of {sorted(mapping)}"
            )
        return cls.parse(mapping[suffix])

    # ------------------------------------------------------------------
    # Serialisation
    # ------------------------------------------------------------------

    def __str__(self) -> str:
        """Return the canonical qualifier string; round-trips with :meth:`parse`."""
        fmt = self.format
        pkg = self.packaging
        cnt = self.content

        # Minimal form: omit qualifier when it equals the defaults.
        if fmt in VECTOR_FORMATS:
            # Default for vectors: packaging=D, content=O
            if pkg == Packaging.D and cnt == Content.O:
                return fmt
            cnt_str = cnt.value if cnt is not None else ""
            return f"{fmt}-{pkg.value}{cnt_str}"
        else:
            # Bitmap: default is just packaging=D (no content)
            if pkg == Packaging.D:
                return fmt
            return f"{fmt}-{pkg.value}"

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def is_vector(self) -> bool:
        return self.format in VECTOR_FORMATS

    @property
    def is_bitmap(self) -> bool:
        return self.format in BITMAP_FORMATS


# ---------------------------------------------------------------------------
# Hints
# ---------------------------------------------------------------------------

_VALID_HINTS: dict[str, Hint] = {h.value: h for h in Hint}


@dataclass(frozen=True, slots=True)
class Hints:
    """Ordered collection of backend preference hints."""

    preferences: tuple[Hint, ...] = ()

    @classmethod
    def parse(cls, s: str | None | Iterable[str | Hint]) -> Hints:
        """Parse hints from various input forms.

        - ``None`` → empty Hints
        - ``str`` → split on comma, strip whitespace, coerce each token to Hint
        - iterable of str or Hint → coerce each element
        Raises :exc:`InvalidInput` on unknown hint codes.
        """
        if s is None:
            return cls()

        tokens: Iterable[str | Hint]
        if isinstance(s, str):
            tokens = [t.strip() for t in s.split(",") if t.strip()]
        else:
            tokens = s

        prefs: list[Hint] = []
        for token in tokens:
            if isinstance(token, Hint):
                prefs.append(token)
            else:
                key = token.lower()
                if key not in _VALID_HINTS:
                    raise InvalidInput(
                        f"Unknown hint {token!r}; expected one of {sorted(_VALID_HINTS)}"
                    )
                prefs.append(_VALID_HINTS[key])

        return cls(preferences=tuple(prefs))

    def pick(self, candidates: Sequence[Hint]) -> Hint | None:
        """Return the first preference that appears in *candidates*, or None."""
        candidate_set = set(candidates)
        for hint in self.preferences:
            if hint in candidate_set:
                return hint
        return None

    def __bool__(self) -> bool:
        return len(self.preferences) > 0
