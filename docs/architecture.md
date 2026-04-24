# Architecture rationale

(Template-level rationale. The scaffolded project ships its own `docs/architecture.md` with the
diagram — this file explains *why* the template is shaped this way.)

## Hexagonal-lite, not hexagonal

Full ports-and-adapters carries real overhead: separate projects per layer, dependency injection
containers, service locators. For a single-MCU firmware project that's not worth it.

"Lite" keeps the spirit:

- **One compilation unit per role.** `core/` is one ESP-IDF component. `adapters_esp32/` is one
  component. `adapters_fake/` is one component. No layering DSL.
- **Constructor injection in the composition root.** `main/main.cpp` is the only place adapters
  are constructed. Core code takes ports by reference and never news.
- **No DI container.** If you need one, you've grown beyond this template.

## Why 80 % host-testable

`pio test -e native` compiles `core/` + `adapters_fake/` with GoogleTest and runs on your laptop.
That's tier-1 in the pyramid (`docs/testing-strategy.md`). Feedback is sub-second; agents can
iterate in the inner loop without flashing a board.

The remaining 20 % — ISRs, DMA, FreeRTOS primitives, flash/NVS, sleep/wake — lives in tier-3
(Unity on chip) because it *genuinely cannot* be faked. Agents are pushed to expand tier-1 first;
tier-3 tests require justification in the PR.

## Why ESP-IDF via PlatformIO

- ESP-IDF gives full chip access, Kconfig, coredump, proper C++ support.
- PlatformIO gives the `pio test -e native` infrastructure that makes the hexagonal split
  pay off.
- Arduino framework was rejected because its C++ support is weaker and its abstractions fight
  the HAL approach.

See `adr/0002-esp-idf-via-platformio.md`.

## Why uv

The Python tooling (sim, HIL, codegen) is a uv workspace at the project root. One `.venv/`, one
`uv.lock` — reproducible across machines. `pip` is deliberately disallowed in
`.claude/settings.json` to stop agents from drifting.

See `adr/0003-uv-workspace.md`.
