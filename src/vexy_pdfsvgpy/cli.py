from __future__ import annotations
# this_file: src/vexy_pdfsvgpy/cli.py
"""Fire CLI for vexy-pdfsvgpy."""

from pathlib import Path
from typing import Any

from loguru import logger
from rich.console import Console
from rich.table import Table

from . import __version__, convert as _convert
from .errors import VexyError


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
        hint: str | None = None,
        regularize: bool = False,
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
        """Convert one file to another format. Format inferred from extension."""
        self._configure_logging(verbose)
        if input is None or output is None:
            self._console.print("[red]Error:[/red] --input and --output are required")
            return 2
        # Build options dict, omitting None values and False booleans to avoid
        # passing unsupported kwargs to backends that don't accept them.
        options: dict[str, Any] = {}
        for key, val in {
            "regularize": regularize,
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

    def split(self, input: str, out_dir: str, *, verbose: bool = False) -> int:
        """Split a multi-page PDF into one file per page."""
        self._configure_logging(verbose)
        try:
            from .operations import reshape
            pages = reshape.pages2docs_pdf(Path(input), Path(out_dir))
            self._console.print(
                f"[green]Split {input} into {len(pages)} page(s) in {out_dir}[/green]"
            )
            return 0
        except Exception as e:
            self._console.print(f"[red]Error:[/red] {e}")
            return 1

    def merge(self, inputs: str, output: str, *, verbose: bool = False) -> int:
        """Merge multiple PDFs (comma-separated paths) into one."""
        self._configure_logging(verbose)
        try:
            from .operations import reshape
            srcs = [Path(p.strip()) for p in inputs.split(",") if p.strip()]
            out = reshape.docs2pages_pdf(srcs, Path(output))
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
