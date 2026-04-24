# Embedded coding rules

Hexagonal structure, `Result<T, E>`, exceptions/RTTI off, clang-format — all table-stakes. The
rules below are the *embedded-specific* ones: things an agent writing code for a 240 MHz chip
with 512 KB of RAM will silently violate if not told. Rules marked **(H)** are enforced by a
pre-commit hook; the rest are prose and are policed by the `code-reviewer` sub-agent.

## Memory

1. **No dynamic allocation after `app_main()` returns.** Heap fragments kill long-running
   firmware. Prefer `std::array<N>`, fixed-size ring buffers, and object pools. `std::string`,
   `std::map`, `std::vector::push_back` are banned in `core/` hot paths.
2. **(H) Stack-size budget per task.** Every `xTaskCreate*` call must read its stack size from
   a named `constexpr uint32_t <name>_STACK_BYTES` so budgets are reviewable. Enforced by
   `.claude/hooks/stack-size-convention.sh`.
3. **PSRAM placement is explicit.** Use `EXT_RAM_BSS_ATTR` for large static buffers, `DRAM_ATTR`
   for ISR-touched data, `RTC_DATA_ATTR` for deep-sleep-persistent state, `IRAM_ATTR` for ISR
   handlers. Default: don't annotate unless you've thought about it.
4. **DMA buffer alignment.** ESP32-S3 DMA wants 4-byte alignment (16-byte for some peripherals).
   Mandate `alignas(16) std::array<uint8_t, N>` for any buffer handed to I²S/SPI/UART DMA.
5. **No non-trivial globals.** All adapters are constructed in the composition root
   (`main/main.cpp`). Static init order bites otherwise.
6. **`constexpr` / `consteval` first.** Register maps, pin tables, protocol constants —
   compile-time. No runtime `std::map` for fixed lookup tables.

## Types

7. **C++ is statically typed — Python must be too.** `mypy --strict` runs in pre-commit over
   `tools/`. The hook covers `tools/codegen`, `tools/sim/simhost`, `tools/hil/hil`. Add type
   stubs or `py.typed` markers as needed — do not use `# type: ignore` without a comment that
   explains why.
8. **`enum class` over `enum`** and over `#define` for states, error codes, modes. Prefer
   `uint8_t` underlying for enums that are also wire formats.
9. **Strong typedefs for units.** `struct Milliseconds { uint32_t v; };`, `struct Volts { float v; };`.
   Stops the agent from adding a duration to a voltage. Cheap.
10. **No implicit int→GPIO conversions.** `board::X_PIN` is `constexpr int` from codegen; wrap
    in a `Pin` struct when adding new APIs so callers must say `.num()`. Pre-commit already
    rejects bare GPIO literals via `no-magic-gpio.sh`.

## Naming & files

11. **File naming is PascalCase for C++** (`IClock.hpp`, `ClockEsp32.cpp`) — one class per file,
    file name tracks class name. Python stays snake_case. See `CLAUDE.md`.
12. **Scoping prefixes.** Interfaces `I<Name>` (IClock, II2cBus). Fakes `Fake<Name>` (FakeClock).
    Real adapters suffix `Esp32` (ClockEsp32). Per-chip drivers live at
    `components/drivers/<chip>/` with class name `<Chip>Driver`.
13. **Member vars trailing underscore** (`now_`, `bus_`). Constants `SCREAMING_SNAKE_CASE` for
    codegen output, `kCamelCase` for in-code literals. Pick one per file and stay consistent.
14. **Verbose over terse.** `sample_buffer` not `buf`, `i2c_clock_speed_hz` not `spd`. Agents
    write better code with full names, and reviewers spot bugs faster.

## Comments

15. **Default: no comments.** Good names + static types carry the intent.
16. **Required comments (not hook-enforced — reviewer prompt):**
    - `// Datasheet §X.Y p.N` on any line that manipulates a device register with a magic value.
    - `// Why: …` on any non-obvious decision: ISR-safe sequencing, volatile ordering, MMIO
      fences, magic timing constants, memory-attribute choices.
    - `// Invariant: …` at the top of state-machine transition functions, listing what must
      hold on entry.
    - Doxygen-style one-line `///` on every port method. The port is a contract; every
      implementer and every reader benefits from the contract being in the header.

## Concurrency & ISRs

17. **(H) No `ESP_LOGx`, `malloc`, `new`, `std::string`, `std::vector` inside `IRAM_ATTR`
    functions.** Enforced by `.claude/hooks/isr-hygiene.sh`. Use `ESP_EARLY_LOGx` or post a
    message to a queue that a task drains.
18. **ISR handlers are `IRAM_ATTR` and implicitly `noexcept`** (exceptions are off anyway). Keep
    them short; do the heavy work in a task.
19. **Cross-ISR/task state goes through FreeRTOS primitives** (`xQueueSendFromISR`,
    `xSemaphoreGiveFromISR`, task notifications). `volatile` is for MMIO only — it is NOT a
    synchronization primitive.
20. **No `std::thread`, `std::mutex`, `std::condition_variable`.** Add ports (`IMutex`,
    `IQueue`, `ITask`) that wrap FreeRTOS primitives so core code stays host-testable.

## Errors & logging

21. **Every `Result<T, E>` is consumed.** `Result` is `[[nodiscard]]` so dropping one compiles
    with a warning; treat the warning as an error in CI.
22. **Log once per error, at the boundary where it becomes actionable.** Convention:
    - Driver: returns `Result::Err`, does not log.
    - Adapter: logs `W` on recoverable fault, `E` on terminal.
    - Use case / composition: logs `E` only if user-visible.

    Agents love to sprinkle logs at every layer — the reviewer rejects this.
23. **Per-component log levels** live in `logging.cpp` (in `main/` alongside `main.cpp`):

    ```cpp
    void configure_logging() {
        esp_log_level_set("*",    ESP_LOG_INFO);
        esp_log_level_set("imu",  ESP_LOG_DEBUG);
        esp_log_level_set("wifi", ESP_LOG_WARN);
    }
    ```

    Call it first thing in `app_main()`.
