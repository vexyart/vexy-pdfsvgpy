import re

with open('src/vexy_pdfsvgpy/__init__.py', 'r') as f:
    content = f.read()

convert_regex = r"def convert\(\s*input: str \| Path \| None = None,\s*output: str \| Path \| None = None,\s*\*,\s*hints: str \| Hints \| None = None,\s*\*\*options: Any,\s*\) -> Path:.*?def execute"
convert_new = """def convert(
    input: str | Path | None = None,
    output: str | Path | None = None,
    *,
    vinput: str | None = None,
    voutput: str | None = None,
    binput: str | None = None,
    boutput: str | None = None,
    hints: str | Hints | None = None,
    **options: Any,
) -> Path:
    \"\"\"High-level conversion entry point.

    Resolves FormatSpecs from explicit specifiers or file extensions,
    plans the pipeline, and executes it. Returns the output path.
    \"\"\"
    if input is None or output is None:
        raise InvalidInput("convert() requires both 'input' and 'output'")
    src = Path(input)
    dst = Path(output)
    if not src.exists() and not src.is_dir():
        # Will handle glob/recursive search later
        pass

    # Basic logic for resolving FormatSpecs based on IDEA.md
    input_spec = None
    output_spec = None

    if vinput:
        input_spec = FormatSpec.parse(vinput)
    elif binput:
        input_spec = FormatSpec.parse(binput)
    
    if voutput:
        output_spec = FormatSpec.parse(voutput)
    elif boutput:
        output_spec = FormatSpec.parse(boutput)

    # Fallback to extension if explicit specs are not provided
    if not input_spec:
        try:
            input_spec = FormatSpec.from_extension(src)
        except InvalidInput:
            if src.is_dir():
                raise InvalidInput("Must specify explicit format specifier (e.g. --binput png_d) for directories")
            raise

    if not output_spec:
        output_spec = FormatSpec.from_extension(dst)

    # If --input is a bitmap, it's used as --binput. If vector, --vinput.
    # Currently handled implicitly since FormatSpec.from_extension resolves to the right FormatSpec.

    resolved_hints = Hints.parse(hints) if not isinstance(hints, Hints) else hints
    steps = plan(input_spec, output_spec, resolved_hints, options=options)
    return execute(steps, src, dst)

def execute"""

content = re.sub(convert_regex, convert_new, content, flags=re.DOTALL)

with open('src/vexy_pdfsvgpy/__init__.py', 'w') as f:
    f.write(content)
