import re

with open('pyproject.toml', 'r') as f:
    content = f.read()

# Add optional dependencies
extras = """[project.optional-dependencies]
cairo = [
    "CairoSVG",
]
ghostscript = [
    "ghostscript",
]
all = [
    "vexy-pdfsvgpy[cairo]",
    "vexy-pdfsvgpy[ghostscript]",
]

[project.scripts]"""

content = content.replace("[project.scripts]", extras)

with open('pyproject.toml', 'w') as f:
    f.write(content)
