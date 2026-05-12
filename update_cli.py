import re

with open('src/vexy_pdfsvgpy/cli.py', 'r') as f:
    content = f.read()

# Fix split
split_regex = r"def split\(self, input: str, out_dir: str, \*, verbose: bool = False\) -> int:.*?(?=\n    def)"
split_new = """def split(self, input: str, out_dir: str | None = None, *, verbose: bool = False) -> int:
        \"\"\"Split a multi-page PDF into one file per page.\"\"\"
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
            return 1"""

content = re.sub(split_regex, split_new, content, flags=re.DOTALL)

# Fix merge
merge_regex = r"def merge\(self, inputs: str, output: str, \*, verbose: bool = False\) -> int:.*?(?=\n    def)"
merge_new = """def merge(self, inputs: str, output: str | None = None, *, verbose: bool = False) -> int:
        \"\"\"Merge multiple PDFs (comma-separated paths) into one.\"\"\"
        self._configure_logging(verbose)
        try:
            from .operations import reshape

            srcs = [Path(p.strip()) for p in inputs.split(",") if p.strip()]
            if not srcs:
                raise ValueError("No input files provided")
            
            if output:
                out_path = Path(output)
            else:
                out_path = srcs[0].parent / f"{srcs[0].stem}-merged.pdf"
                
            out = reshape.docs2pages_pdf(srcs, out_path)
            self._console.print(f"[green]Merged {len(srcs)} file(s) into {out}[/green]")
            return 0
        except Exception as e:
            self._console.print(f"[red]Error:[/red] {e}")
            return 1"""

content = re.sub(merge_regex, merge_new, content, flags=re.DOTALL)

with open('src/vexy_pdfsvgpy/cli.py', 'w') as f:
    f.write(content)
