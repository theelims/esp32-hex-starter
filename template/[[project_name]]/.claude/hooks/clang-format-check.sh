#!/usr/bin/env bash
set -euo pipefail
for f in "$@"; do
    diff -u "$f" <(clang-format "$f") || {
        echo "❌ $f is not clang-format clean. Run: clang-format -i $f"
        exit 1
    }
done
