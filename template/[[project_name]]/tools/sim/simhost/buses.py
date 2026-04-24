"""Skeleton for Python-side bus simulators.

Filled in on demand — default tests use the C++ fakes.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict


@dataclass
class I2cBus:
    """Simple register-bank I2C simulator.

    Each device is a callable (register_write, register_read) pair
    registered on a 7-bit address.
    """
    devices: Dict[int, "I2cDevice"] = field(default_factory=dict)

    def attach(self, addr: int, device: "I2cDevice") -> None:
        self.devices[addr] = device

    def write(self, addr: int, data: bytes) -> None:
        self.devices[addr].on_write(data)

    def read(self, addr: int, length: int) -> bytes:
        return self.devices[addr].on_read(length)


class I2cDevice:
    def on_write(self, data: bytes) -> None: ...
    def on_read(self, length: int) -> bytes:
        return b"\x00" * length


class SpiBus:
    """Stub — implement when the first real SPI scenario lands."""
