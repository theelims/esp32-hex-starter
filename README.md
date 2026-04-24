# esp32-hex-starter

A [Copier](https://copier.readthedocs.io/) template for scaffolding an **ESP32-S3 hexagonal-lite firmware project** optimised for agentic coding with Claude Code.

The generated project uses:

- **ESP-IDF via PlatformIO** (C++17, exceptions/RTTI off).
- **Ports & Adapters** so ~80% of the firmware is host-testable with GoogleTest.
- **uv** as the Python package manager for sim and HIL tooling.
- **Claude Code integration**: `CLAUDE.md`, sub-agents, skills, hooks, MCP.
- Optional **HIL bench** (Siglent SDS1104X-E + Nordic PPK2).

## Scaffold a new project

```bash
uvx copier copy gh:theelims/esp32-hex-starter my-project
cd my-project
uv sync
uv run pre-commit install
uv run pre-commit install --hook-type pre-push
pio run -e esp32s3
```

Copier will ask a short series of questions (project name, board variant, whether to include HIL and MCP). Defaults target the ESP32-S3 DevKitC-N16R8.

## Update an existing project

From inside a previously-scaffolded project, pull in upstream template fixes:

```bash
copier update
```

Copier walks conflicting hunks interactively — the same diff3-style flow as a rebase.

## What's in the template

- `template/{{project_name}}/` — every file that gets materialised into the new project. File names or contents that depend on answers use `.jinja` extensions.
- `docs/` — rationale, architecture notes, ADRs, testing & debugging strategy. Users read this after scaffolding; the agent does not "execute" it.
- `scripts/` — post-generation and verification helpers.
- `tests/` — pytest suite that copies the template into a scratch directory and asserts it compiles and native tests pass.
- `.github/workflows/scaffold-matrix.yml` — CI matrix over answer combinations.

## History

Originally prose in a 2500-line `SETUP.md`. The migration to Copier is documented in `docs/adr/0004-copier-migration.md`.

## License

MIT. See `LICENSE`.
