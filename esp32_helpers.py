"""ESP32 part-number parsing and partition-layout helpers.

This module is the canonical source of truth for ``parse_part_number`` and
``partition_layout``. Tests import from here; the scaffolded project gets a
copy at ``tools/esp32_helpers.py`` for runtime use.
"""

from __future__ import annotations

import re
from typing import Any

_PART_NUMBER_RE = re.compile(
    r"^ESP32"
    r"(?:-(?P<family>C\d+|S\d+|H\d+|P\d+))?"
    r"-(?P<package>WROOM|WROVER|MINI|SOLO)"
    r"-(?P<package_rev>\d+)"
    r"(?P<external_antenna>U)?"
    r"(?:-(?P<temp>[NH])(?P<flash>\d+)"
    r"(?:R(?P<psram>\d+)(?P<low_voltage>V)?)?"
    r")?$"
)


def parse_part_number(part_number: str) -> dict[str, Any]:
    """Decode an Espressif module part number into structured fields.

    Raises ``ValueError`` on input that does not match the documented grammar.
    """
    if not isinstance(part_number, str):
        raise ValueError(f"part_number must be a string, got {type(part_number).__name__}")

    m = _PART_NUMBER_RE.match(part_number.strip())
    if not m:
        raise ValueError(
            f"Unrecognised Espressif part number: {part_number!r}. "
            "Expected something like 'ESP32-S3-WROOM-1-N16R8'."
        )

    family = m.group("family")
    package = m.group("package")
    package_rev = m.group("package_rev")
    external_antenna = m.group("external_antenna") == "U"
    temp = m.group("temp")
    flash_str = m.group("flash")
    psram_str = m.group("psram")
    low_voltage = m.group("low_voltage") == "V"

    if family is None:
        chip = "esp32"
        chip_pretty = "ESP32"
    else:
        chip = f"esp32{family.lower()}"
        chip_pretty = f"ESP32-{family.upper()}"

    package_name = f"{package}-{package_rev}"

    flash_size_mb = int(flash_str) if flash_str else 0
    psram_present = psram_str is not None
    psram_size_mb = int(psram_str) if psram_str else 0

    if not psram_present:
        psram_mode = "none"
    elif psram_size_mb >= 8:
        psram_mode = "octal"
    else:
        psram_mode = "quad"

    if low_voltage and not psram_present:
        raise ValueError(
            f"Invalid part number {part_number!r}: 'V' suffix only appears on "
            "modules with PSRAM."
        )
    if temp == "H" and package not in {"WROOM", "WROVER"}:
        raise ValueError(
            f"Invalid part number {part_number!r}: high-temp 'H' suffix only "
            "exists for WROOM and WROVER packages."
        )

    if package == "WROOM" and package_rev == "2":
        flash_mode = "opi"
    else:
        flash_mode = "qio"

    vdd_spi_v = 1.8 if low_voltage else 3.3
    flash_freq_mhz = 80
    temp_grade = "high" if temp == "H" else "normal"

    return {
        "chip": chip,
        "chip_pretty": chip_pretty,
        "package": package_name,
        "external_antenna": external_antenna,
        "temp_grade": temp_grade,
        "flash_size_mb": flash_size_mb,
        "psram_present": psram_present,
        "psram_size_mb": psram_size_mb,
        "psram_mode": psram_mode,
        "vdd_spi_v": vdd_spi_v,
        "flash_mode": flash_mode,
        "flash_freq_mhz": flash_freq_mhz,
    }


_KB = 1024
_MB = 1024 * 1024


def _row(name: str, type_: str, subtype: str, offset: int, size: int) -> dict[str, Any]:
    return {
        "name": name,
        "type": type_,
        "subtype": subtype,
        "offset": f"0x{offset:X}",
        "size": f"0x{size:X}",
    }


_NVS_OFFSET = 0x9000
_NVS_SIZE = 0x6000
_OTADATA_OFFSET = 0xF000
_OTADATA_SIZE = 0x2000
_PHY_OFFSET = 0x11000
_PHY_SIZE = 0x1000
_APP_ALIGN = 0x10000


def _align_up(value: int, alignment: int) -> int:
    remainder = value % alignment
    return value if remainder == 0 else value + (alignment - remainder)


def _layout_default(flash_bytes: int) -> list[dict[str, Any]]:
    factory_size = {4 * _MB: 0x180000, 8 * _MB: 0x300000, 16 * _MB: 0x600000, 32 * _MB: 0x600000}[flash_bytes]
    factory_offset = _align_up(_PHY_OFFSET + _PHY_SIZE, _APP_ALIGN)
    storage_offset = factory_offset + factory_size
    storage_size = flash_bytes - storage_offset
    return [
        _row("nvs", "data", "nvs", _NVS_OFFSET, _NVS_SIZE),
        _row("otadata", "data", "ota", _OTADATA_OFFSET, _OTADATA_SIZE),
        _row("phy_init", "data", "phy", _PHY_OFFSET, _PHY_SIZE),
        _row("factory", "app", "factory", factory_offset, factory_size),
        _row("storage", "data", "spiffs", storage_offset, storage_size),
    ]


def _layout_ota(flash_bytes: int) -> list[dict[str, Any]]:
    ota_size = {4 * _MB: 0x140000, 8 * _MB: 0x300000, 16 * _MB: 0x600000, 32 * _MB: 0x600000}[flash_bytes]
    ota_0_offset = _align_up(_PHY_OFFSET + _PHY_SIZE, _APP_ALIGN)
    ota_1_offset = ota_0_offset + ota_size
    storage_offset = ota_1_offset + ota_size
    storage_size = flash_bytes - storage_offset
    return [
        _row("nvs", "data", "nvs", _NVS_OFFSET, _NVS_SIZE),
        _row("otadata", "data", "ota", _OTADATA_OFFSET, _OTADATA_SIZE),
        _row("phy_init", "data", "phy", _PHY_OFFSET, _PHY_SIZE),
        _row("ota_0", "app", "ota_0", ota_0_offset, ota_size),
        _row("ota_1", "app", "ota_1", ota_1_offset, ota_size),
        _row("storage", "data", "spiffs", storage_offset, storage_size),
    ]


def _layout_huge_app(flash_bytes: int) -> list[dict[str, Any]]:
    factory_size = {
        4 * _MB: 0x300000,
        8 * _MB: 0x700000,
        16 * _MB: 0xE00000,
        32 * _MB: 0x1E00000,
    }[flash_bytes]
    factory_offset = _align_up(_PHY_OFFSET + _PHY_SIZE, _APP_ALIGN)
    storage_offset = factory_offset + factory_size
    storage_size = flash_bytes - storage_offset
    return [
        _row("nvs", "data", "nvs", _NVS_OFFSET, _NVS_SIZE),
        _row("otadata", "data", "ota", _OTADATA_OFFSET, _OTADATA_SIZE),
        _row("phy_init", "data", "phy", _PHY_OFFSET, _PHY_SIZE),
        _row("factory", "app", "factory", factory_offset, factory_size),
        _row("storage", "data", "spiffs", storage_offset, storage_size),
    ]


_SCHEMES = {
    "default": _layout_default,
    "ota": _layout_ota,
    "huge_app": _layout_huge_app,
}

_SUPPORTED_FLASH_SIZES = {4, 8, 16, 32}


def partition_layout(scheme: str, flash_size_mb: int) -> list[dict[str, Any]] | None:
    """Return the partition table rows for ``scheme`` x ``flash_size_mb``.

    ``scheme == "custom"`` returns ``None`` so the template emits a stub CSV
    with a TODO marker for the user to fill in.

    Raises ``ValueError`` for unknown schemes or unsupported flash sizes.
    """
    if scheme == "custom":
        return None
    if scheme not in _SCHEMES:
        raise ValueError(
            f"Unknown partition scheme: {scheme!r}. "
            f"Expected one of: {sorted(_SCHEMES) + ['custom']}."
        )
    if flash_size_mb not in _SUPPORTED_FLASH_SIZES:
        raise ValueError(
            f"Unsupported flash size: {flash_size_mb} MB. "
            f"Supported: {sorted(_SUPPORTED_FLASH_SIZES)}."
        )

    rows = _SCHEMES[scheme](flash_size_mb * _MB)
    _validate_layout(rows, flash_size_mb * _MB)
    return rows


def _validate_layout(rows: list[dict[str, Any]], flash_bytes: int) -> None:
    last_end = 0
    for r in rows:
        offset = int(r["offset"], 16)
        size = int(r["size"], 16)
        if offset < last_end:
            raise ValueError(f"Partition {r['name']!r} overlaps previous partition.")
        if r["type"] == "app" and offset % _APP_ALIGN != 0:
            raise ValueError(f"Partition {r['name']!r} must be 64KB-aligned (offset=0x{offset:X}).")
        if offset % 0x1000 != 0:
            raise ValueError(f"Partition {r['name']!r} offset must be 4KB-aligned (got 0x{offset:X}).")
        if size <= 0:
            raise ValueError(f"Partition {r['name']!r} has non-positive size {size}.")
        last_end = offset + size
    if last_end > flash_bytes:
        raise ValueError(f"Layout exceeds flash size: {last_end} > {flash_bytes}.")
