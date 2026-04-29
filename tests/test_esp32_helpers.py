"""Unit tests for extensions.esp32_helpers."""

from __future__ import annotations

import pytest

from esp32_helpers import parse_part_number, partition_layout


class TestParsePartNumber:
    def test_n16r8_octal_psram(self) -> None:
        result = parse_part_number("ESP32-S3-WROOM-1-N16R8")
        assert result["chip"] == "esp32s3"
        assert result["chip_pretty"] == "ESP32-S3"
        assert result["package"] == "WROOM-1"
        assert result["external_antenna"] is False
        assert result["temp_grade"] == "normal"
        assert result["flash_size_mb"] == 16
        assert result["psram_present"] is True
        assert result["psram_size_mb"] == 8
        assert result["psram_mode"] == "octal"
        assert result["vdd_spi_v"] == 3.3
        assert result["flash_mode"] == "qio"

    def test_n16r8v_low_voltage(self) -> None:
        result = parse_part_number("ESP32-S3-WROOM-1-N16R8V")
        assert result["vdd_spi_v"] == 1.8
        assert result["psram_mode"] == "octal"

    def test_n8r2_quad_psram(self) -> None:
        result = parse_part_number("ESP32-S3-WROOM-1-N8R2")
        assert result["flash_size_mb"] == 8
        assert result["psram_size_mb"] == 2
        assert result["psram_mode"] == "quad"

    def test_n4_no_psram(self) -> None:
        result = parse_part_number("ESP32-S3-WROOM-1-N4")
        assert result["flash_size_mb"] == 4
        assert result["psram_present"] is False
        assert result["psram_size_mb"] == 0
        assert result["psram_mode"] == "none"

    def test_external_antenna_u_suffix(self) -> None:
        result = parse_part_number("ESP32-S3-WROOM-1U-N16R8")
        assert result["external_antenna"] is True

    def test_wroom_2_uses_octal_flash(self) -> None:
        result = parse_part_number("ESP32-S3-WROOM-2-N16R8")
        assert result["flash_mode"] == "opi"
        assert result["package"] == "WROOM-2"

    def test_mini_1_n4(self) -> None:
        result = parse_part_number("ESP32-S3-MINI-1-N4")
        assert result["package"] == "MINI-1"
        assert result["flash_mode"] == "qio"

    def test_c6_chip(self) -> None:
        result = parse_part_number("ESP32-C6-MINI-1-N4")
        assert result["chip"] == "esp32c6"
        assert result["chip_pretty"] == "ESP32-C6"

    def test_high_temp_h_suffix(self) -> None:
        result = parse_part_number("ESP32-S3-WROOM-1-H4")
        assert result["temp_grade"] == "high"
        assert result["flash_size_mb"] == 4

    def test_invalid_v_suffix_without_psram_rejected(self) -> None:
        with pytest.raises(ValueError, match="V"):
            parse_part_number("ESP32-S3-WROOM-1-N16V")

    def test_invalid_high_temp_on_mini_rejected(self) -> None:
        with pytest.raises(ValueError, match="high-temp"):
            parse_part_number("ESP32-S3-MINI-1-H4")

    def test_garbage_input_rejected(self) -> None:
        with pytest.raises(ValueError, match="Unrecognised"):
            parse_part_number("not a part number")

    def test_non_string_rejected(self) -> None:
        with pytest.raises(ValueError, match="must be a string"):
            parse_part_number(42)  # type: ignore[arg-type]


class TestPartitionLayout:
    @pytest.mark.parametrize("scheme", ["default", "ota", "huge_app"])
    @pytest.mark.parametrize("flash_size_mb", [4, 8, 16, 32])
    def test_layout_well_formed(self, scheme: str, flash_size_mb: int) -> None:
        rows = partition_layout(scheme, flash_size_mb)
        assert rows is not None
        assert len(rows) >= 4

        last_end = 0
        seen_app = False
        for r in rows:
            offset = int(r["offset"], 16)
            size = int(r["size"], 16)
            assert offset >= last_end, f"row {r['name']} overlaps"
            assert offset % 0x1000 == 0, f"row {r['name']} not 4K aligned"
            if r["type"] == "app":
                assert offset % 0x10000 == 0, f"app row {r['name']} not 64K aligned"
                seen_app = True
            assert size > 0
            last_end = offset + size
        assert seen_app, "every layout must include at least one app partition"
        assert last_end <= flash_size_mb * 1024 * 1024

    def test_ota_has_two_app_slots(self) -> None:
        rows = partition_layout("ota", 16)
        assert rows is not None
        app_names = {r["name"] for r in rows if r["type"] == "app"}
        assert app_names == {"ota_0", "ota_1"}

    def test_default_has_factory_and_storage(self) -> None:
        rows = partition_layout("default", 16)
        assert rows is not None
        names = {r["name"] for r in rows}
        assert "factory" in names
        assert "storage" in names

    def test_huge_app_storage_is_small(self) -> None:
        rows = partition_layout("huge_app", 16)
        assert rows is not None
        storage = next(r for r in rows if r["name"] == "storage")
        factory = next(r for r in rows if r["name"] == "factory")
        assert int(factory["size"], 16) > int(storage["size"], 16)

    def test_custom_returns_none(self) -> None:
        assert partition_layout("custom", 16) is None

    def test_unknown_scheme_rejected(self) -> None:
        with pytest.raises(ValueError, match="Unknown partition scheme"):
            partition_layout("bogus", 16)

    def test_unsupported_flash_size_rejected(self) -> None:
        with pytest.raises(ValueError, match="Unsupported flash size"):
            partition_layout("default", 7)
