# Changelog

All notable changes to this template. Users doing `copier update` should read the
entries between their `_commit` and `HEAD` to know what changed.

Format: [Keep a Changelog](https://keepachangelog.com/en/1.1.0/). Versions are
calendar-based (`YYYY.MM.DD`) — the template is not semver.

## [Unreleased]

### Added
- Initial Copier template migrated from the 2500-line `SETUP.md` in
  `esp32-agent-template/`.
- Questions: `project_name`, `project_description`, `author_name`, `author_email`,
  `board_variant`, `psram_mode`, `flash_size_mb`, `hil_instruments`, `enable_mcp`,
  `cpp_standard`.
- Hexagonal-lite scaffold: `components/core/`, `components/adapters_esp32/`,
  `components/adapters_fake/`, `components/board/`, `components/drivers/`.
- Pre-commit hooks: `core-purity`, `clang-format`, `stack-size-convention`,
  `isr-hygiene`, `no-magic-gpio`, `gen-pins-fresh`, `mypy-tools`; native tests
  gated at push time.
- `.claude/` scaffolding: settings, five sub-agents (hal-author, driver-author,
  test-writer, code-reviewer, component-onboarder), hook scripts.
- Python tooling under `tools/sim/` and optional `tools/hil/`.
- ESP32-S3 coredump + GDB integration via built-in USB-JTAG.
- ADRs 0001–0004.

### Migration notes
- Users coming from `SETUP.md` should delete the old file and re-scaffold with
  `copier copy` into a scratch dir, then merge their local edits manually.
