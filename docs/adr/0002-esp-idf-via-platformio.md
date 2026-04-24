# ADR 0002 — ESP-IDF via PlatformIO

- Status: accepted
- Date: 2026-04-24

## Context

Two mainstream ways to build for ESP32-S3: raw ESP-IDF (`idf.py`) and Arduino-ESP32 (or a
hybrid via Arduino-as-component). The template needs the richer chip access (Kconfig,
coredump, proper C++, FreeRTOS primitives) that only ESP-IDF gives.

Additionally, the template's testability hinges on `pio test -e native` — a native (host)
environment that compiles `core/` + `adapters_fake/` with GoogleTest. PlatformIO gives that
out of the box.

## Decision

- **ESP-IDF** as the firmware framework.
- **PlatformIO** as the build driver, test runner, and debug-adapter host.
- Three PIO environments: `native`, `esp32s3`, `test_esp32s3`.

`debug_tool = esp-builtin` uses the S3's built-in USB-JTAG probe — no external hardware.

## Consequences

- Full ESP-IDF feature set available (Kconfig, sdkconfig, coredump, FreeRTOS, etc.).
- Native tests and target tests share the same CLI (`pio test -e <env>`).
- Debugger entry point is `pio debug`, not a raw `launch.json` — see `docs/debugging.md`.
- PIO manages its own venv at `~/.platformio/penv`, independent of the uv workspace.

## Alternatives considered

- **Raw `idf.py`.** Rejected: no native GoogleTest environment; would have to build one
  manually, which is the opposite of what the template is for.
- **Arduino framework.** Rejected: weaker C++ support, weaker chip control, abstractions
  fight the HAL approach.
- **CMake-only with ESP-IDF toolchain.** Rejected: loses the PIO-level testing infra.
