"""Golden-file verifier.

Walks a scaffolded project and prints a deterministic sha256 over
`find . -type f | sort | xargs sha256sum`. CI pins this hash for the
default-answers run.

Usage:
    uv run python scripts/verify_scaffold.py /path/to/scaffolded-project
"""

from __future__ import annotations

import hashlib
import sys
from pathlib import Path

IGNORE_DIRS = {".git", ".pio", ".venv", "__pycache__", ".pytest_cache"}


def _iter_files(root: Path):
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        parts = set(path.relative_to(root).parts)
        if parts & IGNORE_DIRS:
            continue
        yield path


def fingerprint(root: Path) -> str:
    digest = hashlib.sha256()
    for path in _iter_files(root):
        rel = path.relative_to(root).as_posix()
        digest.update(rel.encode())
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("usage: verify_scaffold.py <scaffolded_project_root>", file=sys.stderr)
        return 2
    root = Path(argv[1]).resolve()
    if not root.is_dir():
        print(f"not a directory: {root}", file=sys.stderr)
        return 2
    print(fingerprint(root))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
