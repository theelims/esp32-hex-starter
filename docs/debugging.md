# Debugging

Two flows: on-target (GDB over the S3 built-in USB-JTAG) and host-side (CodeLLDB on native
GoogleTest binaries).

## On-target debugging (GDB via built-in USB-JTAG)

**Entry point is `pio debug`**, not a raw `launch.json`. PlatformIO starts OpenOCD for the S3
built-in probe when `debug_tool = esp-builtin`; the VS Code launch entry is
`type: platformio-debug`.

Three workflows:

### 1. Interactive attach

```bash
pio debug --interface=gdb -x .gdbinit
```

Halts at `app_main`, step/next/continue, inspect variables. Project `.gdbinit` (add one as you
grow into debugging needs) can auto-load `firmware.elf`, define pretty-printers for
`core::Result<T, E>` and the common fakes, and add a `panic` macro that dumps registers + task
list.

### 2. Post-mortem coredump

Crashes trigger a coredump to flash (`CONFIG_ESP_COREDUMP_ENABLE=y`, set in
`sdkconfig.defaults`). Extract:

```bash
uv run python -m esp_idf_coredump info_corefile -t elf \
  -c coredump.elf .pio/build/esp32s3/firmware.elf
xtensa-esp32s3-elf-gdb .pio/build/esp32s3/firmware.elf coredump.elf
```

### 3. Panic backtrace decode

The boot log from a crashed board prints raw addresses. The `gdb-diagnose` sub-agent (optional;
add one when you hit your first panic) accepts the pasted panic block on stdin and returns an
annotated backtrace — internally it shells out to `xtensa-esp32s3-elf-addr2line`.

## Native-test debugging (CodeLLDB)

CodeLLDB is for **host-side GoogleTest binaries**, not Xtensa targets. The VS Code launch entry
points at `.pio/build/native/program` with a `--gtest_filter` input prompt, so breakpoint-
debugging a single test is one click.

Workflow:

1. Set a breakpoint in the core `.cpp` under test.
2. Run "Debug native test (CodeLLDB)" from the Run & Debug pane.
3. Enter the filter (e.g. `FakeI2c.ScriptedRegisterReadback`) at the prompt.
4. The `pio: build native` preLaunchTask rebuilds; LLDB attaches.
