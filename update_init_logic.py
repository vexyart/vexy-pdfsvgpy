import re

with open('src/vexy_pdfsvgpy/__init__.py', 'r') as f:
    content = f.read()

# Replace convert
convert_regex = r"def convert\(.*?return execute\(steps, src, dst\)"
convert_new = """def _gather_inputs(src: Path, fmt: str, pkg: Packaging, recursive: bool, glob_pat: str | None) -> list[Path]:
    if pkg != Packaging.D:
        if src.is_dir():
            raise InvalidInput(f"Input is a directory but format packaging is {pkg.value} (expected 'd')")
        return [src]

    if not src.is_dir():
        # If packaging is D but a single file is provided, treat it as a collection of 1
        return [src]

    # Handle extensions based on format
    exts = []
    if fmt == "pdf":
        exts = [".pdf"]
    elif fmt == "svg":
        exts = [".svg"]
    elif fmt == "png":
        exts = [".png"]
    elif fmt == "jpg":
        exts = [".jpg", ".jpeg"]
    
    files = []
    
    if glob_pat:
        # Use provided glob pattern
        for p in src.glob(glob_pat):
            if p.is_file() and (not exts or p.suffix.lower() in exts):
                files.append(p)
    elif recursive:
        # Recursive search
        for ext in exts:
            files.extend(src.rglob(f"*{ext}"))
            files.extend(src.rglob(f"*{ext.upper()}"))
    else:
        # Non-recursive search
        for ext in exts:
            files.extend(src.glob(f"*{ext}"))
            files.extend(src.glob(f"*{ext.upper()}"))
            
    return sorted(list(set(files)))

def convert(
    input: str | Path | None = None,
    output: str | Path | None = None,
    *,
    vinput: str | None = None,
    voutput: str | None = None,
    binput: str | None = None,
    boutput: str | None = None,
    hints: str | Hints | None = None,
    **options: Any,
) -> Path | list[Path]:
    \"\"\"High-level conversion entry point.

    Resolves FormatSpecs from file extensions, plans the pipeline, and
    executes it. Returns the output path.
    \"\"\"
    if input is None or output is None:
        raise InvalidInput("convert() requires both 'input' and 'output'")
    src = Path(input)
    dst = Path(output)
    if not src.exists():
        raise InvalidInput(f"input does not exist: {src}")

    if vinput is not None:
        input_spec = FormatSpec.parse(vinput)
    elif binput is not None:
        input_spec = FormatSpec.parse(binput)
    else:
        if src.is_dir():
            raise InvalidInput("Must specify explicit format specifier (e.g. --binput png_d) for directories")
        input_spec = FormatSpec.from_extension(src)

    if voutput is not None:
        output_spec = FormatSpec.parse(voutput)
    elif boutput is not None:
        output_spec = FormatSpec.parse(boutput)
    else:
        output_spec = FormatSpec.from_extension(dst)
        
    resolved_hints = Hints.parse(hints) if not isinstance(hints, Hints) else hints
    
    # Check if we need to process multiple files
    recursive = options.pop("recursive", False)
    glob_pat = options.pop("glob", None)
    
    input_files = _gather_inputs(src, input_spec.format, input_spec.packaging, recursive, glob_pat)
    
    if not input_files:
        raise InvalidInput(f"No matching files found in {src}")
        
    if len(input_files) == 1:
        steps = plan(input_spec, output_spec, resolved_hints, options=options)
        
        # If output packaging is D and dst is a dir (or we're outputting a dir)
        out_path = dst
        if output_spec.packaging == Packaging.D and (dst.is_dir() or not dst.suffix):
            dst.mkdir(parents=True, exist_ok=True)
            out_path = dst / f"{input_files[0].stem}.{output_spec.format}"
            
        return execute(steps, input_files[0], out_path)
        
    # We have multiple files
    # Note: Full implementation of document composition (docs2pages, docs2layers) 
    # would go here based on output_spec.packaging.
    # For now, we'll just process them individually if output is D
    
    if output_spec.packaging == Packaging.D:
        dst.mkdir(parents=True, exist_ok=True)
        results = []
        for in_file in input_files:
            steps = plan(input_spec, output_spec, resolved_hints, options=options)
            out_file = dst / f"{in_file.stem}.{output_spec.format}"
            results.append(execute(steps, in_file, out_file))
        return results
        
    else:
        # TODO: docs2pages (m) or docs2layers (l)
        # We would convert each file to a temporary vector format, then merge them
        raise NotImplementedError(f"Combining multiple inputs into {output_spec.packaging.value} is not fully implemented yet")"""

content = re.sub(convert_regex, convert_new, content, flags=re.DOTALL)

with open('src/vexy_pdfsvgpy/__init__.py', 'w') as f:
    f.write(content)
