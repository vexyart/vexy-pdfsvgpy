import re

with open('src/vexy_pdfsvgpy/cli.py', 'r') as f:
    content = f.read()

convert_regex = r"def convert\(.*?\)\s*->\s*int:"
convert_new = """def convert(
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
    ) -> int:"""

content = re.sub(convert_regex, convert_new, content, flags=re.DOTALL)

# Add text_as to options
options_regex = r"\"regularize\": regularize,"
options_new = """"regularize": regularize,
            "text_as": text_as,"""

content = re.sub(options_regex, options_new, content, flags=re.DOTALL)

with open('src/vexy_pdfsvgpy/cli.py', 'w') as f:
    f.write(content)
