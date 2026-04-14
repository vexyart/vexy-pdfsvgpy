#!/usr/bin/env bash
set -euo pipefail
fd -e py -x uvx autoflake -i {} \;
fd -e py -x uvx pyupgrade --py312-plus {} \;
fd -e py -x uvx ruff check --output-format=github --fix --unsafe-fixes {} \;
fd -e py -x uvx ruff format --respect-gitignore --target-version py312 {} \;
uvx hatch test
