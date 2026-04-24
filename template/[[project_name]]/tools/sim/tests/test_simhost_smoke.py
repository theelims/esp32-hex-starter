from simhost.buses import I2cBus, I2cDevice


class Echo(I2cDevice):
    def __init__(self) -> None:
        self.last = b""

    def on_write(self, data: bytes) -> None:
        self.last = data

    def on_read(self, n: int) -> bytes:
        return self.last[:n] or b"\x00" * n


def test_i2c_round_trip() -> None:
    bus = I2cBus()
    bus.attach(0x42, Echo())
    bus.write(0x42, b"\xDE\xAD")
    assert bus.read(0x42, 2) == b"\xDE\xAD"
