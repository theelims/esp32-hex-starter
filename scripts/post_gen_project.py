"""Post-generation hook.

Runs after Copier has materialised the template. Idempotent — safe to re-run
on `copier update`. Failures are printed but do not abort; the user can fix and
retry manually.

Executed via copier's `_tasks:` key in copier.yml. (Kept here as a script so
tests can import it.)
"""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path


def _which(cmd: str) -> str | None:
    return shutil.which(cmd)


def _run(cmd: list[str], cwd: Path) -> int:
    print(f"  $ {' '.join(cmd)}")
    try:
        return subprocess.run(cmd, cwd=cwd, check=False).returncode
    except FileNotFoundError:
        print(f"  (skipped — {cmd[0]} not on PATH)")
        return 0


def main(project_root: Path) -> int:
    print(f"post_gen_project: finalising {project_root}")

    if _which("uv") is None:
        print("  uv not found — install it from https://astral.sh/uv before continuing.")
        return 0

    _run(["uv", "sync"], cwd=project_root)
    _run(["uv", "run", "pre-commit", "install"], cwd=project_root)
    _run(["uv", "run", "pre-commit", "install", "--hook-type", "pre-push"], cwd=project_root)

    if (project_root / "hardware" / "board.yaml").exists():
        _run(["uv", "run", "gen-pins"], cwd=project_root)

    return 0


if __name__ == "__main__":
    sys.exit(main(Path.cwd()))
