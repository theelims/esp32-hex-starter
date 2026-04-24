# Schematic conventions for the importer

The importer (`uv run import-schematic`) reads a single EAGLE 9.x /
Fusion 360 Electronics `.sch` file and writes into `hardware/board.yaml`.
It cannot guess design intent — it reads explicit annotations.

## Required — `BOARD_*` attributes on parts

For each part that should appear in `board.yaml`, add attributes in
Fusion/EAGLE (Edit → Attribute → Add attribute):

| Attribute         | Values                            | Example        |
|-------------------|-----------------------------------|----------------|
| `BOARD_ROLE`      | stable key used in YAML           | `imu`, `charger`, `user_button` |
| `BOARD_KIND`      | `peripheral` (default) / `gpio`   | `peripheral`   |
| `BOARD_BUS`       | bus name from board.yaml          | `spi2`, `i2c0` |
| `BOARD_ADDR`      | I2C address (hex, 0x..)           | `0x6B`         |
| `BOARD_CS`        | CS net / MCU pad label            | `IMU_CS`       |
| `BOARD_INT1`      | interrupt line 1                  | `IMU_INT1`     |
| `BOARD_INT2`      | interrupt line 2                  | `IMU_INT2`     |
| `BOARD_PIN`       | for `BOARD_KIND=gpio` only        | `USER_BTN`     |
| `BOARD_ACTIVE_LOW`| `true` / `false`                  | `true`         |
| `BOARD_PULL`      | `up` / `down` / `none`            | `up`           |

Only parts with `BOARD_ROLE` are imported. Everything else (passives,
regulators, test points) is ignored by the importer — describe them in
`docs/board.md` if they matter.

## Required — net naming conventions

The importer reads pin assignments by walking from the MCU's pads to
their net names. The net name is the ground truth.

| Net name pattern        | Purpose                               |
|-------------------------|---------------------------------------|
| `I2C<N>_SDA`            | data line for I2C bus N               |
| `I2C<N>_SCL`            | clock line for I2C bus N              |
| `SPI<N>_MOSI`           | master-out for SPI bus N              |
| `SPI<N>_MISO`           | master-in for SPI bus N               |
| `SPI<N>_SCLK`           | clock for SPI bus N                   |
| `<ROLE>_CS`             | chip-select, where ROLE matches BOARD_ROLE |
| `<ROLE>_INT1`, `_INT2`  | interrupt lines                       |
| `<ROLE>_PWR_EN`         | power-enable line                     |

N is `0`, `1`, `2`, ... matching the ESP32-S3 peripheral index.

## Recommended — one schematic sheet per domain

For boards with more than ~30 parts, split across sheets:

- `01-power.sch` — regulators, charger, protection
- `02-mcu.sch` — ESP32-S3 and its passives
- `03-sensors.sch` — IMU, environmental, etc.
- `04-io.sch` — buttons, LEDs, connectors

The importer handles multi-sheet schematics automatically.

## Merge behaviour when you re-import

Running `uv run import-schematic --apply` after a schematic revision:

1. Reads the current `board.yaml` (human edits).
2. Reads the current `.sch` (design truth).
3. Fills blank YAML fields from the schematic.
4. **Flags conflicts** (differences between hand-edited YAML and
   schematic) — never silently overwrites.
5. Writes the merged result only with `--apply`.

Without `--apply`, it's a dry run that just lists what would change
and where the conflicts are. This is the "safe" verb the agent uses
by default.

## Fields the importer cannot fill

These always need human input — they aren't in the schematic:

- `power.battery.max_v` / `min_v`
- `buses.<name>.speed_hz`
- `notes` fields
- `board.name`, `board.revision`
