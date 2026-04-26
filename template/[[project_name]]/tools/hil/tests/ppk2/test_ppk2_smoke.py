import pytest


@pytest.mark.hil
def test_ppk2_reads_zero_when_off(ppk2):
    ppk2.source_mode(voltage_mv=3300)
    samples = ppk2.capture(duration_s=0.5)
    assert samples.mean() < 5000  # < 5 mA while DUT is off-ish
