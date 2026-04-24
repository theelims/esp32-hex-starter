#!/usr/bin/env bash
set -euo pipefail
echo "Running native test suite (pio test -e native)..."
pio test -e native --without-uploading
