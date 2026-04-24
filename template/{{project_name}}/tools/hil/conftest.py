import os

import pytest

from hil.dut import DUT
from hil.ppk2 import PPK2
from hil.scope import SDS1104


@pytest.fixture(scope="session")
def scope():
    addr = os.environ.get("SCOPE_ADDR", "TCPIP::192.168.1.50::INSTR")
    s = SDS1104(addr)
    yield s
    s.close()


@pytest.fixture(scope="session")
def ppk2():
    port = os.environ.get("PPK2_PORT", "/dev/ttyACM1")
    p = PPK2(port)
    yield p
    p.close()


@pytest.fixture()
def dut():
    port = os.environ.get("DUT_PORT", "/dev/ttyACM0")
    d = DUT(port)
    yield d
    d.close()
