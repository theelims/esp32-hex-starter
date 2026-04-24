#!/usr/bin/env bash
# Run the codegen in --check mode. If Pins.hpp is out of date relative to
# hardware/board.yaml, the commit is rejected with an instruction to regenerate.
set -euo pipefail
exec uv run gen-pins --check
