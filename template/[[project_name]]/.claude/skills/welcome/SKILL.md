---
name: welcome
description: Welcome / first-time setup for new scaffolded projects. Asks for the module part number and partition scheme, derives all hardware fields, updates config files, and walks through onboarding.
trigger: /welcome
tools: Read, Write, Edit, Bash, Glob
model: opus
---

# /welcome

You guide the user through first-time setup of a newly scaffolded project.
Execute the steps in order. Do not skip any.

## 1. Gather module part number

Ask the user for their Espressif module part number (e.g. `ESP32-S3-WROOM-1-N16R8`, `ESP32-C6-MINI-1-N4`).

Validate it against this regex before proceeding:
```
^ESP32(-(C|S|H|P)\d+)?-(WROOM|WROVER|MINI|SOLO)-\d+U?(-[NH]\d+(R\d+V?)?)?$
```
If invalid, show the error and ask again.

## 2. Gather partition scheme

Ask the user which partition scheme they want. Choices:
- **default** — single factory app + storage (most common)
- **ota** — two OTA slots + small storage (for field-upgradable firmware)
- **huge_app** — one large factory app, minimal storage (for big binaries)
- **custom** — stub CSV that you fill in later

## 3. Derive values from `tools/esp32_helpers.py`

Run this command:

```bash
uv run python tools/esp32_helpers.py --json "<part_number>"
```

If the helper does not support `--json` mode (no CLI interface), use Python directly:

```bash
uv run python -c "
import sys, json
sys.path.insert(0, 'tools')
from esp32_helpers import parse_part_number, partition_layout
import importlib.util, pathlib
spec = importlib.util.spec_from_file_location('esp32_helpers', 'tools/esp32_helpers.py')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

part = '<user_part_number>'
scheme = '<user_partition_scheme>'

p = mod.parse_part_number(part)
rows = mod.partition_layout(scheme, p['flash_size_mb'])
out = {'parsed': p, 'rows': rows}
print(json.dumps(out))
"
```

Record the result. These are the fields you will write.

### Derived fields you now have

From `parse_part_number`:
| Field | Example |
|-------|---------|
| chip | `esp32s3` |
| chip_pretty | `ESP32-S3` |
| package | `WROOM-1` |
| external_antenna | `false` |
| temp_grade | `normal` |
| flash_size_mb | `16` |
| psram_present | `true` |
| psram_size_mb | `8` |
| psram_mode | `octal` |
| vdd_spi_v | `3.3` |
| flash_mode | `qio` |
| flash_freq_mhz | `80` |

From `partition_layout`:
- CSV rows for the partition table (or `None` if `custom`).

## 4. Show summary for confirmation

Present a compact summary to the user:

```
MCU:               <chip_pretty> (<part_number>)
Flash:             <flash_size_mb>MB, <flash_mode> @ <flash_freq_mhz>MHz
PSRAM:             <psram_mode> <psram_size_mb>MB (or "None")
Partition scheme:  <scheme>
VDD_SPI:           <vdd_spi_v>V
CPU freq:          240 MHz  (hardcoded default)
Console baud:      115200  (hardcoded default)
```

Ask: "Apply these values to all config files?"

## 5. Apply updates

### 5a. `hardware/board.yaml`

Use `Edit` to update these sections:
- `module.part_number` → the user's part number
- `module.chip` → `chip_pretty`
- `module.package` → `package`
- `module.external_antenna` → `external_antenna`
- `module.temp_grade` → `temp_grade`
- `memory.flash.size_mb` → `flash_size_mb`
- `memory.flash.mode` → `flash_mode`
- `memory.flash.freq_mhz` → `flash_freq_mhz`
- `memory.flash.voltage_v` → `vdd_spi_v`
- `memory.psram.present` → `psram_present`
- `memory.psram.size_mb` → `psram_size_mb`
- `memory.psram.mode` → `psram_mode`

Keep `clock`, `power`, `usb`, `console`, `programming`, `buses`, `peripherals`, `gpios` unchanged.

### 5b. `sdkconfig.defaults`

Read the file. Update these lines:
- `CONFIG_ESPTOOLPY_FLASHSIZE_*MB=y` → set to `CONFIG_ESPTOOLPY_FLASHSIZE_<flash_size_mb>MB=y`
- PSRAM section: if `psram_present` is true, set `CONFIG_SPIRAM_MODE_<OCT|QUAD>=y`. If false, replace the PSRAM block with `# No PSRAM on this module variant.\n`.
- `CONFIG_ESP_DEFAULT_CPU_FREQ_MHZ_*` → set to `CONFIG_ESP_DEFAULT_CPU_FREQ_MHZ_240=y`
- Comment at top → update the part number reference

If the helper returned `rows` (not `None` for `custom`), the CSV is handled in step 5c.

### 5c. `partitions.csv`

If `rows` is `None` (custom scheme), write a TODO stub:
```
# TODO(custom): fill in your partition layout here.
# Name, Type, SubType, Offset, Size, Flags
```

If `rows` has data, write the partition entries exactly as returned. Preserve the header comment with scheme and flash size.

### 5d. `boards/<project_name>.json`

Find the board manifest via `glob("**/boards/*.json")` — there should be exactly one.

Update these fields:
- `build.f_cpu` → `"240000000L"` (always 240 MHz)
- `build.f_flash` → `"<flash_freq_mhz>000000L"`
- `build.flash_mode` → `"<flash_mode>"`
- `build.mcu` → `"<chip>"`
- `build.variant` → `"<chip>"`
- `build.extra_flags` → include `"-DBOARD_HAS_PSRAM"` only if `psram_present` is true; remove if not.
- `connectivity` → keep `"wifi"`. Remove `"bluetooth"` if chip is `esp32c6` or `esp32h2`.
- `debug.openocd_target` → `"<chip>.cfg"`
- `name` → `"<project_name> (<part_number>)"`
- `upload.flash_size` → `"<flash_size_mb>MB"`
- `upload.maximum_size` → `<flash_size_mb * 1024 * 1024>`

### 5e. `CLAUDE.md`

Update the MCU line in the **## Hardware** section. Replace the line starting with `- MCU:` with:
```
- MCU: <part_number>, <flash_size_mb> MB flash[% if psram_mode != 'none' %], <psram_mode> PSRAM[% endif %]
```

## 6. Post-scaffold setup

### 6a. Install dependencies
Run:
```bash
uv sync
```

### 6b. Install pre-commit hooks
```bash
uv run pre-commit install
uv run pre-commit install --hook-type pre-push
```

### 6c. Generate pins
```bash
uv run gen-pins
```

### 6d. Verify with native tests
```bash
pio test -e native
```

Report the result. If tests pass, celebrate. If tests fail, show the error and offer to help diagnose.

## 7. Next steps

Tell the user about the remaining skills available:
- `/board-onboarder` — import pins from your EAGLE schematic into `hardware/board.yaml`
- `/component-onboarder` — ingest a chip datasheet and generate driver scaffolding
- Sub-agents in `.claude/agents/` — specialized reviewers and authors

Stop after reporting. Do not write application code or drivers.
