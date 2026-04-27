# esp32-hex-starter

A [Copier](https://copier.readthedocs.io/) template for scaffolding an **ESP32-S3 hexagonal-lite firmware project** optimised for agentic coding. e.g. Claude Code, Codex, OpenCode, Gemini CLI, ...

The generated project uses:

- **ESP-IDF via PlatformIO** (C++, exceptions/RTTI off).
- **Ports & Adapters** so ~80% of the firmware is host-testable with GoogleTest.
- **uv** as the Python package manager for sim and HIL tooling.
- **Claude Code integration**: `CLAUDE.md`, sub-agents, skills, hooks.
- Optional **HIL bench** (Siglent SDS1104X-E + Nordic PPK2 + sigrok logic analyser — multiselect).

## Motivation

Embedded firmware is traditionally built with a tight coupling between application logic and vendor SDK calls. That makes unit testing impossible on a laptop: every code change requires a flash-and-pray cycle on real hardware. For a human developer this is slow. For an AI coding agent it is lethal. Agents iterate in tight loops; if the inner loop takes minutes, context windows burn and quality collapses.

Beyond speed, agents lack implicit embedded intuition. They will dynamically allocate after `app_main()` returns, pick arbitrary stack sizes, and place non-trivial globals wherever compiles. They will guess GPIO numbers, hallucinate I2C addresses, and invent peripherals that do not exist. Without guardrails, an agent will write C++ that looks correct and silently corrupts heap or hard-faults in production.

The cost structure of writing code has shifted dramatically. An agent can generate a clean state machine, refactor a messy driver into ports and adapters, or write fifty unit tests in the time it takes a human to check a single register value in a datasheet. Conversely, an agent has no bodily sense of a 512 KB RAM limit; it will cheerfully `std::vector::push_back` its way to a heap exhaustion crash because "it compiled." What is hard for a human (boilerplate, exhaustive tests, mechanical refactoring) is trivial for an agent. What is hard for an agent (memory layout, timing, pin assignments, power budgets) is easy for a human with a schematic and a scope.

This template rethinks embedded development for agentic workflows by amplifying the agent's strengths and containing its weaknesses:

1. **Sub-second feedback** — the majority of logic is compiled and tested natively with GoogleTest, letting the agent iterate on structure and behaviour at machine speed.
2. **Hardware truth** — pin maps, register maps, and schematic intent live in version-controlled files the agent reads, not guesses. The human provides the ground truth; the agent consumes it.
3. **Enforced constraints** — pre-commit hooks and coding rules stop agents from violating memory, stack, and ISR contracts before the code ever reaches a board. The human defines the limits; the agent operates inside them.
## Architecture & Philosophy

### Hexagonal-lite

Full ports-and-adapters (DI containers, service locators, layer-per-project) is overkill for a single-MCU firmware. "Lite" keeps the testability without the ceremony:

- **`components/core/`** — pure C++, no ESP-IDF or Arduino includes. Ports (interfaces) live here.
- **`components/adapters_esp32/`** — real ESP-IDF bindings. The only place hardware headers are allowed.
- **`components/adapters_fake/`** — in-memory fakes used by GoogleTest on the host.
- **`main/main.cpp`** — the composition root. Adapters are constructed here and injected by reference into core code. No DI container.

This split is enforced by a pre-commit hook: any `#include` of an ESP-IDF header under `core/` fails CI. The result is ~80% of the firmware running in `pio test -e native` on a laptop. The remaining 20% (ISRs, DMA, FreeRTOS primitives, flash/NVS, sleep/wake) genuinely cannot be faked and lives in on-target Unity tests. Agents are pushed to expand the host-testable layer first.

See [`docs/architecture.md`](docs/architecture.md) for the full rationale, and [`docs/adr/0001-hexagonal-lite.md`](docs/adr/0001-hexagonal-lite.md) for the decision record.

### Testing Pyramid

The project ships four test tiers, used in strict proportion:

| Tier | Mechanism | When to use |
|---|---|---|
| 1 | Native GoogleTest + fakes | Default. Every new behaviour starts here. |
| 2 | Python device simulation | Scenarios painful in C++: recorded sensor traces, fault injection. |
| 3 | On-target Unity (flash + run) | ISRs, DMA, FreeRTOS, hardware-clocked timing only. |
| 4 | HIL bench (scope + power probe) | Electrical behaviour, deep-sleep current, end-to-end protocol. |

A PR that is 90% tier-3 with no tier-1 is a red flag. The `code-reviewer` sub-agent enforces this balance.

See [`docs/testing-strategy.md`](docs/testing-strategy.md) for the full pyramid and coverage/fuzzing options.

### Tooling Choices

**ESP-IDF via PlatformIO** gives full chip access (Kconfig, coredump, FreeRTOS) and the native test infrastructure that makes the hexagonal split pay off. Arduino framework was rejected for weaker C++ support and abstractions that fight the HAL approach. See [`docs/adr/0002-esp-idf-via-platformio.md`](docs/adr/0002-esp-idf-via-platformio.md).

**uv** manages the Python tooling (sim, HIL, codegen) as a single workspace with one lockfile. `pip` is deliberately disallowed to stop agents from drifting. See [`docs/adr/0003-uv-workspace.md`](docs/adr/0003-uv-workspace.md).

**Debugging** covers both on-target (GDB over the S3 built-in USB-JTAG) and host-side (CodeLLDB on native GoogleTest binaries), plus post-mortem coredump decode. See [`docs/debugging.md`](docs/debugging.md).

### Hardware Knowledge Pipeline

Architecture without facts is aspiration. The scaffold provides three layers of hardware knowledge, ordered by how often they change:

1. **Board facts** (`hardware/board.yaml`) — pin map, bus assignments. Regenerates `components/board/include/board/Pins.hpp`. Enforced by hooks: stale generated code is rejected, and raw GPIO literals in source are banned.
2. **Component facts** (`hardware/datasheets/<chip>/`) — register maps, command sets, protocols. A `component-onboarder` sub-agent ingests the PDF and produces structured reference and a skill template before the `driver-author` writes any code.
3. **Schematic intent** (`docs/board.md`) — design rationale, power budgets, gotchas from hard-won experience.

See [`docs/hardware-knowledge.md`](docs/hardware-knowledge.md) for the full pipeline.

### Embedded Coding Rules

The [`docs/embedded-coding-rules.md`](docs/embedded-coding-rules.md) document is the contract between you and the agent. It covers memory (no heap after init, explicit stack budgets, DMA alignment), types (strong typedefs for units, `enum class`), naming, comments, concurrency, and logging. Rules marked **(H)** are enforced by pre-commit hooks; the rest are policed by the `code-reviewer` sub-agent.

## Scaffold a new project

```bash
uvx copier copy gh:theelims/esp32-hex-starter my-project
cd my-project
uv sync
uv run pre-commit install
uv run pre-commit install --hook-type pre-push
pio run -e esp32s3
```

Copier will ask a short series of questions (project name, board variant, which HIL bench instruments to include). Defaults target the ESP32-S3 DevKitC-N16R8 with scope + PPK2.

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

## License

MIT. See [`LICENSE`](LICENSE).
