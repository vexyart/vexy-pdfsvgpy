---
this_file: WORK.md
---

# Work log

The tag-triggered Release workflow builds and checks the wheel and sdist, then uploads them through PyPI Trusted Publishing. The local release script delegates to that workflow. PyPI returned HTTP 404 for version 0.0.6 during this review. See PLAN.md for the release and remaining development checks.

## Latest verification

- `bash -n publish.sh` passed. Live publication requires the owner's PyPI publisher configuration.
- `./build.sh docs` rebuilt the fly-january 0.2.1 site in strict mode with zero warnings.
- `uv run --locked pytest -q --cov=vexy_pdfsvgpy` passed all 219 tests with 82% coverage and seven deprecation warnings.
- Ruff lint passed, Ruff found all 50 files formatted, and strict mypy passed for all 26 source files.
