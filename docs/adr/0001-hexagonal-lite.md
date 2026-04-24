# ADR 0001 — Hexagonal-lite for ESP32-S3 firmware

- Status: accepted
- Date: 2026-04-24

## Context

Embedded firmware projects tend to couple application logic directly to vendor SDK calls
(`esp_*`, `driver/*`, Arduino). That makes unit testing impossible on a laptop — every test
needs a flashed board. For an agentic-coding workflow, a sub-second feedback loop is the
whole game.

Full Ports-and-Adapters is overkill for a single-MCU project: DI containers, layer
projects, service locators. "Hexagonal-lite" is the compromise.

## Decision

Three-tier layout:

- `components/core/` — pure C++17, no ESP-IDF or Arduino includes. Ports live here.
- `components/adapters_esp32/` — real ESP-IDF bindings. The only place hardware headers
  are allowed.
- `components/adapters_fake/` — in-memory fakes used by GoogleTest on the host.

Constructor injection at the composition root (`main/main.cpp`). No DI container.

The rule is enforced by `.claude/hooks/enforce-core-purity.sh` — any `#include` of an
ESP-IDF or Arduino header under `components/core/` fails pre-commit.

## Consequences

- ~80 % of firmware is host-testable in tier 1 (native GoogleTest + fakes).
- Porting to a different ESP32 variant or a different MCU touches only `adapters_esp32/`.
- Adding a peripheral is always: port → fake → real adapter → driver → tests. The
  `hal-author` sub-agent enforces this order.

## Alternatives considered

- **Full hexagonal.** Rejected: the DI overhead doesn't pay for itself on a project with
  one composition root.
- **Flat structure (no ports).** Rejected: gives up the testability that the rest of the
  template is built around.
