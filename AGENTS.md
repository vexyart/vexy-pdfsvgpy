# AGENTS.md

Guidance for AI coding agents working in this repo. See `CLAUDE.md` for the full architectural notes; this file is the short operational contract.

## Build & verify

```bash
uv sync --dev
uv run ruff check --fix src tests
uv run ruff format src tests
uv run mypy src/vexy_pdfsvgpy
uv run pytest -q --cov=vexy_pdfsvgpy
```

All four must pass before you claim a change is done. Tests read committed fixtures from `tests/fixtures/` — regenerate with `uv run python tests/fixtures/_generate.py`.

## Rules

- Every source file starts with a `# this_file: <path>` marker after the module docstring.
- One deterministic backend per capability; do not add backends that need Cairo, Poppler, or Ghostscript at the core (see `CLAUDE.md` and `SPEC.md`).
- Versioning is `hatch-vcs` from git tags — never hand-edit a version. Release via `uvx gitnextver@latest .`.
- Keep the public API (`convert`, `FormatSpec`, backend function names) stable; tests depend on it.
