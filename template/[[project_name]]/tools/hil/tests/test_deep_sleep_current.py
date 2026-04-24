import time

import pytest

from hil.analysis import mean_current_ua


@pytest.mark.hil
def test_deep_sleep_under_20uA(dut, ppk2):
    ppk2.source_mode(voltage_mv=3300)
    time.sleep(0.3)
    dut.expect_ok("deep_sleep 5")
    time.sleep(1.0)  # skip entry transient
    samples = ppk2.capture(duration_s=3.0)
    avg = mean_current_ua(samples)
    assert avg < 20.0, f"deep sleep average = {avg:.2f} µA"
