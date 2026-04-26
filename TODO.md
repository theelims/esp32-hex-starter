# TODO — esp32-hex-starter follow-ups

Tracking work deferred from the Stage-3 Copier migration. Items are roughly
ordered from "needed before first real use" to "nice to have".

## Before first real use

- [x] **Verify copier `_exclude` works** with the custom `[% %]` delimiters for
      `tools/hil/**` and `.mcp.json` gating. `tests/test_scaffold.py` confirms both
      `enable_hil=false` and `enable_mcp=false` correctly drop the excluded paths.
- [x] **Run the test matrix locally.** Fast tier (`pytest`) passes; 2 slow tests skip because
      PlatformIO is not installed. No regressions from the Copier-delimiter fixes.
- [ ] **Pin the GitHub slug.** `README.md` still references `theelims/esp32-hex-starter`.
      Replace with the actual org/repo when the template is pushed.
- [ ] **Publish to a git remote** and sanity-run `uvx copier copy gh:<org>/<repo> /tmp/demo`
      with `project_name=demo_board`. Verify it produces a tree that compiles.

## Content the prose referenced but never defined

The original SETUP.md mentioned these by name but never provided content. Add
on first real need, not speculatively:

- [ ] **`.gdbinit`** at scaffolded-project root — auto-load `firmware.elf`,
      pretty-printers for `core::Result<T, E>` and `fakes::FakeI2cBus`, a `panic`
      macro that dumps registers + task list. See `docs/debugging.md` § "Interactive attach".
- [ ] **`tools/decode_backtrace.py`** — accepts a pasted panic block on stdin,
      runs `xtensa-esp32s3-elf-addr2line` per frame, prints `file:line` per frame.
      See `docs/debugging.md` § "Panic backtrace decode".
- [ ] **`.claude/agents/gdb-diagnose.md`** — sub-agent that wraps `decode_backtrace.py`.
      User pastes panic log → agent returns annotated backtrace + hypothesis.
- [ ] **`main/logging.cpp`** — centralises per-tag ESP_LOG levels. See
      `docs/embedded-coding-rules.md` rule 23. Scaffold as a stub whose
      `configure_logging()` is called first thing in `app_main()`.
- [ ] **`components/adapters_esp32/src/LoggerEspLog.cpp`** — real `ILogger`
      implementation that forwards to `ESP_LOGx` with a tag. Referenced in
      `docs/testing-strategy.md` § ESP_LOG conventions.

## Coverage & fuzzing (opt-in)

Mentioned in `docs/testing-strategy.md` as "two cheap additions, off by default":

- [ ] **`[env:native_cov]`** in `platformio.ini.jinja` with `--coverage` build
      flag, plus `tools/coverage.sh` that drives `lcov` → HTML report. Target
      ≥80 % line coverage on `components/core/`.
- [ ] **`[env:fuzz]`** in `platformio.ini.jinja` with
      `-fsanitize=fuzzer,address,undefined` for libFuzzer on any parser or
      protocol decoder in core.

## Nice-to-have template improvements

- [x] **C6 board variant.** `board_variant = esp32-c6-devkitc-1` is a questionnaire
      option and `platformio.ini.jinja` already branches on it (board, psram_mode
      conditional). Needs real C6 hardware to validate the generated `sdkconfig.defaults`.
- [x] **`enable_hil=false` scaffolded project still imports `hil` in
      root pyproject.** Verified: `pyproject.toml.jinja` guards both
      `[tool.uv.workspace].members` and `[tool.mypy].files` with `[% if enable_hil %]`.
- [ ] **`.claude/skills/esp32s3-reference/SKILL.md`** was removed from the tree
      per A1/B10 of the review. Consider adding a minimal chip-reference skill
      (power tree, GPIO quirks, DMA channels) so the agent has S3-general
      knowledge on hand without a chip-specific onboard.
- [ ] **`ISpiBus` fake** — `FakeSpiBus.hpp` to parallel `FakeI2cBus.hpp`. Currently
      only the port exists.
- [ ] **Golden-file hash** in `tests/test_scaffold.py` — the scaffolding
      currently asserts structure but doesn't pin `scripts/verify_scaffold.py`'s
      sha256 to a known value. Capture the hash of the default-answers run
      into `tests/fixtures/default_answers.sha256` and assert on it.
- [ ] **Copier `_message_before_copy`** — one-line heads-up before questions
      start: "This scaffolds an ESP32-S3 hexagonal firmware project. Takes ~60s."

## Documentation gaps

- [ ] **Upgrade path from existing SETUP.md projects.** `CHANGELOG.md` says
      "delete the old file and re-scaffold into a scratch dir, then merge" —
      write a `docs/migrating-from-setup-md.md` that walks through it.
- [ ] **Per-chip skill template.** `.claude/agents/component-onboarder.md`
      describes the SKILL.md shape but there's no worked example. Ship one
      (e.g. BMP280) under `docs/examples/` so users see the format.
- [ ] **`docs/mcp.md` install URLs are placeholders** (`<org>`). Replace with
      vetted sources once the MCP servers you actually use are decided.

## Governance

- [ ] **Tag the first release.** `CHANGELOG.md` is currently under `[Unreleased]`
      — cut `2026.04.24` once the template lands in a remote repo and CI passes.
- [ ] **Add `CONTRIBUTING.md`** — one page on how to propose changes, how the
      CI matrix works, and why the answer set is intentionally small.
