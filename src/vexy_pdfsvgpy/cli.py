from __future__ import annotations

# this_file: src/vexy_pdfsvgpy/cli.py
"""Fire CLI for vexy-pdfsvgpy."""

from pathlib import Path
from typing import Any

from loguru import logger
from rich.console import Console
from rich.table import Table

from . import __version__
from . import convert as _convert
from .errors import InvalidInput, VexyError
from .types import FormatSpec


class CLI:
    """vexy-pdfsvgpy: unified PDF / SVG / PNG conversion."""

    def __init__(self) -> None:
        self._console = Console()

    def version(self) -> str:
        """Print the version string."""
        return __version__

    def convert(
        self,
        input: str | None = None,
        output: str | None = None,
        *,
        vinput: str | None = None,
        voutput: str | None = None,
        binput: str | None = None,
        boutput: str | None = None,
        recursive: bool = False,
        glob: str | None = None,
        hint: str | None = None,
        regularize: bool = False,
        text_as: str | None = None,
        dim: str | None = None,
        scale: str | None = None,
        top: float | None = None,
        bottom: float | None = None,
        left: float | None = None,
        right: float | None = None,
        crop: str | None = None,
        gray: bool = False,
        invert: bool = False,
        vivid: float | None = None,
        bright: float | None = None,
        contrast: float | None = None,
        backdrop: str | None = None,
        verbose: bool = False,
    ) -> int:
        """Convert one file to another format. Format inferred from extension or specified via --vinput/--binput/--voutput/--boutput."""
        self._configure_logging(verbose)
        if input is None or output is None:
            self._console.print("[red]Error:[/red] --input and --output are required")
            return 2
        # Build options dict, omitting None values and False booleans to avoid
        # passing unsupported kwargs to backends that don't accept them.
        options: dict[str, Any] = {}
        for key, val in {
            "recursive": recursive,
            "glob": glob,
            "regularize": regularize,
            "text_as": text_as,
            "dim": dim,
            "scale": scale,
            "top": top,
            "bottom": bottom,
            "left": left,
            "right": right,
            "crop": crop,
            "gray": gray,
            "invert": invert,
            "vivid": vivid,
            "bright": bright,
            "contrast": contrast,
            "backdrop": backdrop,
        }.items():
            if val is not None and val is not False:
                options[key] = val
        try:
            out_path = _convert(
                input=input,
                output=output,
                vinput=vinput,
                voutput=voutput,
                binput=binput,
                boutput=boutput,
                hints=hint,
                **options,
            )
        except VexyError as e:
            self._console.print(f"[red]{type(e).__name__}:[/red] {e}")
            return 1
        self._print_summary(Path(input), out_path)
        return 0

    def regularize(
        self, input: str, output: str, *, hint: str | None = None, verbose: bool = False
    ) -> int:
        """Shortcut: `convert --regularize`."""
        return self.convert(input=input, output=output, hint=hint, regularize=True, verbose=verbose)

    def split(self, input: str, out_dir: str | None = None, *, verbose: bool = False) -> int:
        """Split a multi-page PDF into one file per page."""
        self._configure_logging(verbose)
        try:
            from .operations import reshape

            in_path = Path(input)
            out_path = Path(out_dir) if out_dir else in_path.parent
            pages = reshape.pages2docs_pdf(in_path, out_path)
            self._console.print(
                f"[green]Split {input} into {len(pages)} page(s) in {out_path}[/green]"
            )
            return 0
        except Exception as e:
            self._console.print(f"[red]Error:[/red] {e}")
            return 1

    def merge(self, inputs: str, output: str | None = None, *, verbose: bool = False) -> int:
        """Merge multiple PDFs (comma-separated paths) into one."""
        self._configure_logging(verbose)
        try:
            from .operations import reshape

            srcs = [Path(p.strip()) for p in inputs.split(",") if p.strip()]
            if not srcs:
                raise ValueError("No input files provided")

            out_path = Path(output) if output else srcs[0].parent / f"{srcs[0].stem}-merged.pdf"

            out = reshape.docs2pages_pdf(srcs, out_path)
            self._console.print(f"[green]Merged {len(srcs)} file(s) into {out}[/green]")
            return 0
        except Exception as e:
            self._console.print(f"[red]Error:[/red] {e}")
            return 1

    def _configure_logging(self, verbose: bool) -> None:
        logger.remove()
        level = "DEBUG" if verbose else "INFO"
        logger.add(lambda msg: None, level=level)  # no-op sink; Rich handles user output

    def _print_summary(self, src: Path, dst: Path) -> None:
        size = dst.stat().st_size if dst.exists() else 0
        table = Table(title="Conversion complete")
        table.add_column("Input", style="cyan")
        table.add_column("Output", style="green")
        table.add_column("Size", justify="right", style="magenta")
        table.add_row(str(src), str(dst), f"{size:,} B")
        self._console.print(table)


def _make_shortcut(fmt_name: str):
    def _shortcut(self, input: str | None = None, output: str | None = None, **kwargs):
        """Shortcut for `convert --voutput {fmt}`."""
        return self.convert(input=input, output=output, voutput=fmt_name, **kwargs)
    _shortcut.__name__ = fmt_name
    _shortcut.__doc__ = f"Shortcut: `convert --voutput {fmt_name}` (inherits all other options)."
    return _shortcut


def _register_format_shortcuts() -> None:
    formats = ["pdf", "svg", "png", "jpg"]
    packagings = ["d", "m", "l", "s"]
    contents = ["o", "t", "b"]
    candidates: set[str] = set()
    for f in formats:
        candidates.add(f)  # bare
        for p in packagings:
            candidates.add(f"{f}_{p}")  # packaging only
            for c in contents:
                candidates.add(f"{f}_{p}{c}")  # packaging + content
    for name in sorted(candidates):
        if "_" not in name:
            # Skip bare format names — they would shadow builtins/identifiers.
            continue
        try:
            FormatSpec.parse(name)
        except InvalidInput:
            continue
        setattr(CLI, name, _make_shortcut(name))


_register_format_shortcuts()


def main() -> None:
    import sys

    import fire

    # Fire prints the return value but always exits 0; use sys.exit to propagate
    # integer return codes from subcommands.
    result = fire.Fire(CLI)
    if isinstance(result, int):
        sys.exit(result)


if __name__ == "__main__":
    main()
