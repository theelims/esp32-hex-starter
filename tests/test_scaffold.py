"""End-to-end scaffold tests.

Runs `copier copy` into a temp dir with a matrix of answer combinations and
asserts:
  1. Expected files exist.
  2. (Slow, marked) `pio run -e esp32s3` succeeds.
  3. (Slow, marked) `pio test -e native` succeeds.

Steps 2 and 3 are gated behind `--runslow` and skipped in the default CI pass.
"""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import pytest

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
    subprocess.run(cmd, check=True)


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


def test_hil_off_drops_hil_tree(scratch: Path) -> None:
    _copier_copy(scratch, {"project_name": "no_hil", "enable_hil": "false"})
    project = scratch / "no_hil"
    assert not (project / "tools" / "hil").exists()
    assert (project / "tools" / "sim").is_dir()


def test_mcp_off_drops_mcp_config(scratch: Path) -> None:
    _copier_copy(scratch, {"project_name": "no_mcp", "enable_mcp": "false"})
    project = scratch / "no_mcp"
    assert not (project / ".mcp.json").exists()


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
