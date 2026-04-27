# Hardware knowledge pipeline

The scaffold gives the agent a hexagonal architecture, but architecture without facts is
aspiration. Without this layer, agents will guess GPIO numbers, hallucinate I2C addresses, and
invent peripherals that don't exist.

Three layers of hardware knowledge, in order of how often they change:

| Layer | Lives in | Authored by | Updates when |
|---|---|---|---|
| **1. Board facts** — pin map, bus assignments | `hardware/board.yaml` → `components/board/include/board/Pins.hpp` (generated) | EAGLE importer + human edits | Every PCB revision |
| **2. Component facts** — register maps, command sets, protocols | `hardware/datasheets/<chip>/` | `component-onboarder` sub-agent, ingests PDF | Once per chip (stable forever) |
| **3. Schematic intent** — design rationale, gotchas, power tree | `docs/board.md` | Human (you) | When you learn something the hard way |

All three are always in the agent's reach: `CLAUDE.md` points at them, and pre-commit hooks
prevent drift between the YAML, the generated header, and the actual firmware.

## Layer 1 — `hardware/board.yaml`

Machine-readable + human-editable. The EAGLE importer writes unknown fields empty rather than
guessing; you fill them in, then `Pins.hpp` regenerates.

Enforcement:

- `.claude/hooks/gen-pins-fresh.sh` rejects commits where `Pins.hpp` is stale relative to
  `board.yaml`.
- `.claude/hooks/no-magic-gpio.sh` rejects raw GPIO integer literals in source code — the only
  way to reference a pin is through a `board::` constant from the generated header.

Workflow:

- Hand-edit `board.yaml`, run `uv run gen-pins`.
- Or, if you have an EAGLE 9.x / Fusion Electronics schematic with `BOARD_*` attributes (see
  `tools/codegen/SCHEMATIC_CONVENTIONS.md`), run `uv run import-schematic` — dry-run first, then
  `--apply`.

## Layer 2 — `hardware/datasheets/<chip>/`

For each chip on the board:

1. Drop the datasheet PDF at `hardware/datasheets/<chip>/datasheet.pdf`.
2. Invoke the `component-onboarder` sub-agent with that chip name. It produces:
    - `datasheet.md` — relevant excerpts (register map, modes, protocol, interrupts).
    - `register_map.md` — structured register reference.
    - `components/drivers/<chip>/include/<chip>_regs.hpp` — `constexpr` definitions.
    - `.claude/skills/<chip>-driver/SKILL.md` — per-chip skill with a known-good driver template.
3. Only *after* these exist, invoke `driver-author` to write the actual driver.

The `driver-author` sub-agent refuses to start until step 2 is complete.

## Layer 3 — `docs/board.md`

Human-authored narrative. Design intent the schematic cannot express — power budgets, gotchas
from hard-won experience, test-point access, why a particular pin was chosen.

Template: see the scaffolded `docs/board.md`.

