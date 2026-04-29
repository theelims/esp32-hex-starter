"""End-to-end scaffold tests.

Runs `copier copy` into a temp dir with a matrix of answer combinations and
asserts:
  1. Expected files exist.
  2. (Slow, marked) `pio run -e esp32s3` succeeds.
  3. (Slow, marked) `pio test -e native` succeeds.

Steps 2 and 3 are gated behind `--runslow` and skipped in the default CI pass.
"""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

import pytest
import yaml

TEMPLATE_ROOT = Path(__file__).resolve().parent.parent


def pytest_addoption(parser):
    parser.addoption("--runslow", action="store_true", default=False, help="Run slow PIO tests.")


def pytest_collection_modifyitems(config, items):
    if config.getoption("--runslow"):
        return
    skip_slow = pytest.mark.skip(reason="--runslow not given")
    for item in items:
        if "slow" in item.keywords:
            item.add_marker(skip_slow)


def _copier_copy(dst: Path, data: dict[str, str | bool | int]) -> None:
    cmd = ["copier", "copy", "--trust", "--defaults", "--force", str(TEMPLATE_ROOT), str(dst)]
    for key, value in data.items():
        cmd.extend(["--data", f"{key}={value}"])
    import os
    env = os.environ.copy()
    env["PYTHONPATH"] = f"{TEMPLATE_ROOT}{os.pathsep}{env.get('PYTHONPATH', '')}"
    subprocess.run(cmd, check=True, env=env)


@pytest.fixture
def scratch(tmp_path: Path) -> Path:
    (tmp_path / "scratch").mkdir()
    return tmp_path / "scratch"


def test_default_answers_scaffolds(scratch: Path) -> None:
    _copier_copy(scratch, {"project_name": "demo_board"})
    project = scratch / "demo_board"
    assert (project / "platformio.ini").is_file()
    assert (project / "CLAUDE.md").is_file()
    assert (project / "components" / "core" / "include" / "ports" / "IClock.hpp").is_file()
    assert (project / "components" / "adapters_fake" / "include" / "fakes" / "FakeClock.hpp").is_file()


def test_default_board_yaml_has_expanded_sections(scratch: Path) -> None:
    _copier_copy(scratch, {"project_name": "demo_board"})
    project = scratch / "demo_board"
    board = yaml.safe_load((project / "hardware" / "board.yaml").read_text())
    assert board["module"]["part_number"] == "ESP32-S3-WROOM-1-N16R8"
    assert board["module"]["chip"] == "ESP32-S3"
    assert board["module"]["package"] == "WROOM-1"
    assert board["memory"]["flash"]["size_mb"] == 16
    assert board["memory"]["flash"]["mode"] == "qio"
    assert board["memory"]["psram"]["present"] is True
    assert board["memory"]["psram"]["mode"] == "octal"
    assert board["console"]["baud"] == 115200
    assert board["clock"]["cpu_freq_mhz"] == 240
    assert board["usb"]["console"] == "usb_serial_jtag"
    assert board["usb"]["otg_role"] == "none"
    assert board["programming"]["partition_scheme"] == "default"
    # Pinout sections are still present and empty/example-only by default.
    assert "buses" in board
    assert "peripherals" in board
    assert "gpios" in board


def test_derive_strategy_emits_custom_pio_board(scratch: Path) -> None:
    _copier_copy(scratch, {"project_name": "demo_board"})
    project = scratch / "demo_board"
    board_json = project / "boards" / "demo_board.json"
    assert board_json.is_file()
    manifest = json.loads(board_json.read_text())
    assert manifest["build"]["mcu"] == "esp32s3"
    assert manifest["build"]["flash_mode"] == "qio"
    assert manifest["upload"]["flash_size"] == "16MB"
    assert manifest["upload"]["maximum_size"] == 16 * 1024 * 1024
    assert "bluetooth" in manifest["connectivity"]
    assert "extra_flags" in manifest["build"]
    assert "-DBOARD_HAS_PSRAM" in manifest["build"]["extra_flags"]
    assert "board = demo_board" in (project / "platformio.ini").read_text()
    assert "board_dir = ./boards" in (project / "platformio.ini").read_text()


def _parse_partitions_csv(text: str) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = [p.strip() for p in line.split(",")]
        rows.append(
            {
                "name": parts[0],
                "type": parts[1],
                "subtype": parts[2],
                "offset": parts[3],
                "size": parts[4],
            }
        )
    return rows


def test_default_partitions_csv_is_populated(scratch: Path) -> None:
    _copier_copy(scratch, {"project_name": "demo_board"})
    project = scratch / "demo_board"
    csv = (project / "partitions.csv").read_text()
    rows = _parse_partitions_csv(csv)
    names = {r["name"] for r in rows}
    assert {"nvs", "otadata", "phy_init", "factory", "storage"} <= names
    assert len(rows) == 5
    # No TODO marker in the default CSV
    assert "TODO(custom)" not in csv


def test_default_sdkconfig_has_correct_flash(scratch: Path) -> None:
    _copier_copy(scratch, {"project_name": "demo_board"})
    project = scratch / "demo_board"
    sdk_cfg = (project / "sdkconfig.defaults").read_text()
    assert "CONFIG_ESPTOOLPY_FLASHSIZE_16MB=y" in sdk_cfg
    assert "CONFIG_SPIRAM_MODE_OCT=y" in sdk_cfg
    assert "CONFIG_ESP_DEFAULT_CPU_FREQ_MHZ_240=y" in sdk_cfg


def test_claude_md_has_correct_mcu_info(scratch: Path) -> None:
    _copier_copy(scratch, {"project_name": "demo_board"})
    project = scratch / "demo_board"
    claude_md = (project / "CLAUDE.md").read_text()
    assert "ESP32-S3-WROOM-1-N16R8" in claude_md
    assert "16 MB flash" in claude_md
    assert "octal PSRAM" in claude_md


def test_hil_empty_drops_hil_tree(scratch: Path) -> None:
    _copier_copy(scratch, {"project_name": "no_hil", "hil_instruments": "[]"})
    project = scratch / "no_hil"
    assert not (project / "tools" / "hil").exists()
    assert (project / "tools" / "sim").is_dir()


def test_hil_sigrok_only_excludes_scope_and_ppk2(scratch: Path) -> None:
    _copier_copy(scratch, {"project_name": "sigrok_only", "hil_instruments": "[sigrok]"})
    project = scratch / "sigrok_only"
    hil = project / "tools" / "hil"
    assert hil.is_dir()
    assert (hil / "hil" / "sigrok_la.py").exists()
    assert not (hil / "hil" / "scope.py").exists()
    assert not (hil / "hil" / "ppk2.py").exists()
    assert (hil / "tests" / "sigrok").is_dir()
    assert not (hil / "tests" / "scope").exists()
    assert not (hil / "tests" / "ppk2").exists()


def test_log2file_filter(scratch: Path) -> None:
    _copier_copy(scratch, {"project_name": "default_demo"})
    project = scratch / "default_demo"
    pio_ini = (project / "platformio.ini").read_text()
    assert "monitor_filters = log2file" in pio_ini


@pytest.mark.slow
def test_scaffolded_project_builds_native(scratch: Path) -> None:
    if shutil.which("pio") is None:
        pytest.skip("platformio not installed")
    _copier_copy(scratch, {"project_name": "build_check"})
    project = scratch / "build_check"
    subprocess.run(["pio", "test", "-e", "native"], cwd=project, check=True)


@pytest.mark.slow
def test_scaffolded_project_builds_esp32s3(scratch: Path) -> None:
    if shutil.which("pio") is None:
        pytest.skip("platformio not installed")
    _copier_copy(scratch, {"project_name": "firmware_check"})
    project = scratch / "firmware_check"
    subprocess.run(["pio", "run", "-e", "esp32s3"], cwd=project, check=True)
