# Testing strategy

The scaffold ships four test mechanisms (native GoogleTest, Python sim, on-target Unity, HIL
pytest). This document is the glue that says *when to use which*.

## The pyramid

```
                  ┌───────────────────────────────────────┐
                  │ 4 · HIL bench (scope + PPK2)          │  uv run pytest -m hil
                  ├───────────────────────────────────────┤
                  │ 3 · On-target Unity (flash + run)     │  pio test -e test_esp32s3
                  ├───────────────────────────────────────┤
                  │ 2 · Python device simulation          │  uv run pytest tools/sim
                  ├───────────────────────────────────────┤
          fast ↓  │ 1 · Native GoogleTest + fakes         │  pio test -e native
                  └───────────────────────────────────────┘
```

## Rules

- **Tier 1 is the default.** Every new behaviour lives here unless it genuinely requires
  hardware, timing, or RTOS. The `code-reviewer` sub-agent rejects PRs that push logic into
  tier 3+ without justification.
- **Tier 2** compiles `components/core/` as a host shared library and drives it from Python
  (`simhost.buses` wires fake devices; scenarios live in `tools/sim/tests/`). Reserve for
  scenarios painful to express in C++: recorded IMU/ADC traces, fault injection, multi-device
  interaction.
- **Tier 3** (Unity on chip) is only for: ISRs, DMA, FreeRTOS task interactions, flash/NVS,
  sleep/wake, hardware-clocked timing.
- **Tier 4 HIL** is only for: electrical behaviour (rise time, overshoot), power (deep-sleep µA),
  and end-to-end protocol against a real sensor.

A PR's test file mix should look like a pyramid. A PR that's 90% tier 3 tests with no tier 1 is
a red flag.

## ESP_LOG conventions

- `components/core/include/ports/ILogger.hpp` exists with levels `Trace/Debug/Info/Warn/Error`
  (mirrors ESP_LOG 1:1). Core code logs through it, never via `ESP_LOGx` directly.
- `components/adapters_esp32/src/LoggerEspLog.cpp` forwards to `esp_log_write()` with a tag.
  Uses `std::source_location` to embed call-site `[file.cpp:line]` at the end of each line.
- `components/adapters_fake/include/fakes/FakeLogger.hpp` records entries into
  `std::vector<LogEntry>` so tests assert on log content.
- `main/logging.cpp` centralizes per-tag levels (see `embedded-coding-rules.md` rule 23).
  Flipping a chip to verbose is one line.
- HIL tests capture serial logs via `DUT.drain_logs(until_pattern, timeout)` — see
  `tools/hil/hil/dut.py`.

Rules:

- No `ESP_LOGx` inside `IRAM_ATTR` (enforced by `isr-hygiene.sh`).
- No logs inside tight loops — log a summary once per N iterations or once per state change.
- Tag per module; tag names are short lowercase strings matching the component folder
  (e.g. `"imu"`, `"wifi"`).
- `configure_logging()` runtime filters (via `esp_log_level_set`) apply to `LoggerEspLog` only;
  `FakeLogger` always passes all levels to keep native test assertions stable.

## Coverage & fuzzing on native (opt-in)

Two cheap additions, off by default:

- **Coverage**: add `[env:native_cov]` with `build_flags += --coverage` and a
  `tools/coverage.sh` that runs `pio test -e native_cov` then `lcov --capture --directory
  .pio/build/native_cov` → HTML report. Target: ≥ 80 % line coverage on `components/core/`.
- **Fuzz**: add `[env:fuzz]` with `-fsanitize=fuzzer,address,undefined` for libFuzzer on any
  parser or protocol decoder in core. Run locally before merging protocol-touching PRs; not in
  pre-commit.
