# Architecture

## Three tiers

```
┌──────────────────────────────────────────────────────────┐
│ main/main.cpp — composition root                         │
│   wires real adapters into the core at app_main()        │
└──────────────────────────┬───────────────────────────────┘
                           │ constructs
                           ▼
┌──────────────────────────────────────────────────────────┐
│ components/core/  (pure C++, host-testable)              │
│   include/ports/*.hpp   ← abstract interfaces            │
│   include/core/*.hpp    ← Result<T,E>, domain types      │
│   src/*.cpp             ← use cases, state machines      │
└─▲─────────────────────────────────────────────────────▲──┘
  │ implements                                implements│
┌─┴──────────────────────┐              ┌───────────────┴─┐
│ adapters_esp32/        │              │ adapters_fake/  │
│  ESP-IDF bindings      │              │  in-memory, for │
│  real hardware         │              │  GoogleTest     │
└────────────────────────┘              └─────────────────┘
```

## Why

- ~80 % of firmware is pure logic. Hexagonal separation makes that 80 % testable in milliseconds on the host.
- Adding a peripheral = (1) new port, (2) fake, (3) real adapter, (4) driver, (5) tests. Always in that order.
- Moving to a different ESP32 variant or a different MCU entirely touches only `adapters_*/`.

## The rule

`components/core/` may not include any of:
- `<Arduino.h>`
- `esp_*`, `driver/*`, `freertos/*`, `soc/*`, `hal/*`, `sdkconfig`

This is enforced by `.claude/hooks/enforce-core-purity.sh` at pre-commit.
