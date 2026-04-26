import subprocess

import pytest


@pytest.mark.hil
def test_la_enumerates(la):
    """sigrok-cli detects the logic analyser — confirms driver + USB connection."""
    result = subprocess.run(
        ["sigrok-cli", f"--driver={la.driver}", "--scan"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    assert la.driver in result.stdout


@pytest.mark.hil
def test_la_captures_digital(la):
    """Short capture returns the expected channel structure and valid sample values."""
    data = la.capture(channels=["D0", "D1"], duration_s=0.01)
    assert set(data.keys()) == {"D0", "D1"}
    assert len(data["D0"]) > 0
    assert all(v in (0, 1) for v in data["D0"])
