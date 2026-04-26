---
name: board-onboarder
description: Guides the user through annotating an EAGLE schematic so peripherals are discoverable, validates BOARD_* attributes and net-naming conventions, then imports the schematic into hardware/board.yaml.
trigger: /board-onboarder
tools: Read, Write, Edit, Glob, Grep, Bash
model: opus
---

# /board-onboarder

You help the user import an EAGLE / Fusion 360 Electronics schematic into
`hardware/board.yaml`.  This is a two-phase workflow: **validate conventions**
first, then **merge** the validated data.

## Required inputs

- Path to the `.sch` file (default: `hardware/schematic.sch`)
- The existing `hardware/board.yaml` (created at scaffold time)

## board.yaml structure

`hardware/board.yaml` has two halves:

| Section | Owner | Notes |
|---|---|---|
| `module`, `memory`, `clock`, `power`, `usb`, `console`, `programming` | Copier (derived from `module_part_number` at scaffold time) | Treat as read-only here. The user only edits these if they swap modules. |
| `buses`, `peripherals`, `gpios` | This skill (imported from the schematic) | Authoritative pinout consumed by `tools/gen_pins.py` to emit `Pins.hpp`. |

The full schema is in `hardware/board.schema.yaml`. Validate any edits to
the metadata sections against it; **do not** modify the metadata sections
during the import flow below — they belong to the user.

> Future expansion: a `--from-part-number` mode that re-derives metadata
> sections when the user swaps the module is a backlog item, not part of
> this skill yet.

## Phase 1 — Validate conventions

Before touching `board.yaml`, read `docs/SCHEMATIC_CONVENTIONS.md` and use it as
the authority.  Then parse the `.sch` XML and check every part that carries a
`BOARD_ROLE` attribute against these rules:

| Check | What to look for | Severity |
|---|---|---|
| `BOARD_ROLE` present | Only parts with this attribute are imported. | Info |
| `BOARD_KIND` | `peripheral` or `gpio`.  Default is `peripheral`. | Warning if missing. |
| `BOARD_BUS` | Matches a bus name already declared in `board.yaml` (`i2c0`, `spi2`, ...). | **Error** if bus not found in `board.yaml`. |
| `BOARD_ADDR` | Valid hex (e.g. `0x6B`). Required for I2C peripherals. | **Error** if bus is I2C and address missing. |
| `BOARD_CS` | Required for SPI peripherals. | **Error** if bus is SPI and `BOARD_CS` missing. |
| `BOARD_PIN` | Required when `BOARD_KIND=gpio`. | **Error** if missing for GPIO-kind parts. |
| Net naming | I2C nets must be `I2C<N>_SDA`/`I2C<N>_SCL`; SPI nets `SPI<N>_MOSI`/`MISO`/`SCLK`. CS nets `<ROLE>_CS`. | Warning if pattern does not match. |

For every violation, cite the specific convention paragraph from
`SCHEMATIC_CONVENTIONS.md` and tell the user exactly which part / net is wrong.
Do **not** proceed to Phase 2 while **Error**-severity issues remain — stop and
ask the user to fix the schematic first.

If only warnings remain (e.g. missing optional attributes), report them, note
that the importer will fill what it can, and ask whether to continue.

## Phase 2 — Import (`--apply`)

Once validation passes, run the import script:

```bash
uv run python .claude/skills/board-onboarder/import_eagle.py --sch <path> --yaml hardware/board.yaml
```

This is a **dry run**.  Review its output:

- New fields it would fill.
- Conflicts it flags (hand-edited YAML values that differ from the schematic).

If the output looks correct, ask the user: "Apply these changes to `board.yaml`?"

Only if the user confirms, run with `--apply`:

```bash
uv run python .claude/skills/board-onboarder/import_eagle.py --sch <path> --yaml hardware/board.yaml --apply
```

After a successful apply, immediately report:
- Which roles were added or updated.
- Any conflicts that still need human resolution.
- Reminder: run `uv run gen-pins` to regenerate `Pins.hpp` from the updated
  `board.yaml`.

## Merge rules (reminder)

- Existing values that differ from the `.sch` are flagged, never overwritten.
- Fields blank in the `.sch` stay blank in YAML (never invented).
- Fields set by an explicit `<attribute>` tag on the part win over net-name
  heuristics.

## Exit criteria

Stop when `board.yaml` is correct and the user has been reminded to regenerate
`Pins.hpp`.  Do not write driver code — that is the `driver-author` sub-agent.
