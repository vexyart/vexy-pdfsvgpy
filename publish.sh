#!/usr/bin/env bash
# this_file: publish.sh
# Push the release tag. The Release workflow builds and publishes through PyPI OIDC.
set -euo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")"
uvx gitnextver
tag="$(git describe --tags --exact-match HEAD 2>/dev/null || true)"
if [[ ! "$tag" =~ ^v[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
  echo "HEAD carries no vX.Y.Z tag. gitnextver only tags when there are changes to commit." >&2
  exit 1
fi
