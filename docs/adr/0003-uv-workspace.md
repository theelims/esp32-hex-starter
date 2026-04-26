# ADR 0003 — uv workspace for Python tooling

- Status: accepted
- Date: 2026-04-24

## Context

Python tooling in this template includes simulation (`tools/sim/`), HIL bench (`tools/hil/`),
and codegen (`tools/codegen/`). Historically this means multiple venvs, multiple
`requirements.txt` files, and drift between a developer's machine and CI.

`uv` (by Astral) offers a Cargo-like workspace: one lockfile, one venv, all members
installed editable.

## Decision

- Root `pyproject.toml` is a uv workspace. Members: `tools/sim`, `tools/hil` (when
  `hil_instruments` is non-empty), plus root codegen scripts registered under `[project.scripts]`.
- Single `.venv/` at the project root, single `uv.lock` (committed).
- `uv run <cmd>` for everything. No `source .venv/bin/activate`.
- **`pip` is disallowed** in `.claude/settings.json` to stop agents from drifting.
- `mypy --strict` over `tools/` in pre-commit.

## Consequences

- One command (`uv sync`) installs the whole Python-tooling universe.
- `uv.lock` makes "works on my machine" reproducible.
- Agents that try `pip install` get prompted for permission and redirected to `uv add`.
- Python 3.10 is the floor — chosen for modern type syntax without risking ESP-IDF
  compatibility issues on older CI runners.

## Alternatives considered

- **Separate venvs per tool.** Rejected: twice the install time, twice the drift.
- **Poetry.** Rejected: slower, heavier than uv; doesn't offer a clean workspace model.
- **pip + requirements.txt.** Rejected: no lockfile semantics, agents install whatever
  today's PyPI resolves to.
