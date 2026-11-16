#!/usr/bin/env bash
# Regenerates src/styne/_generated (models only) from openapi.yaml.
set -euo pipefail
cd "$(dirname "$0")/.."
work="$(mktemp -d -p "$PWD" .gen.XXXXXX)"
trap 'rm -rf "$work"' EXIT
printf 'project_name_override: styne-sdk\npackage_name_override: _generated\n' > "$work/config.yaml"
openapi-python-client generate --path openapi.yaml --config "$work/config.yaml" --output-path "$work/out" --overwrite
rm -rf src/styne/_generated
mkdir -p src/styne/_generated
cp -r "$work/out/_generated/models" "$work/out/_generated/types.py" "$work/out/_generated/py.typed" src/styne/_generated/
printf '"""Models generated from openapi.yaml. Do not edit by hand."""\n' > src/styne/_generated/__init__.py
# Some generator releases import their HTTP client as httpx2; the SDK depends on httpx.
grep -rl 'httpx2' src/styne/_generated | xargs -r perl -pi -e 's/httpx2/httpx/g'
# The models only need the Unset marker; replace the generated types.py with a minimal copy.
cat > src/styne/_generated/types.py <<'EOF'
"""Marker for fields the server did not send."""

from typing import Literal

from attrs import define


@define
class Unset:
    def __bool__(self) -> Literal[False]:
        return False


UNSET: Unset = Unset()

__all__ = ["UNSET", "Unset"]
EOF

