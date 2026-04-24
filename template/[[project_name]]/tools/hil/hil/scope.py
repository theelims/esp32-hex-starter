"""Siglent SDS1104X-E driver via SCPI over LAN.

Usage:
    scope = SDS1104(address="TCPIP::192.168.1.50::INSTR")
    scope.configure_channel(1, vdiv=1.0, coupling="DC")
    scope.configure_timebase(tdiv=1e-3)
    scope.configure_trigger(channel=1, level=1.5, slope="POS")
    trace = scope.single_capture(channel=1)  # -> numpy float array in volts
"""
from __future__ import annotations

import time

import numpy as np
import pyvisa


class SDS1104:
    def __init__(self, address: str, timeout_ms: int = 10000):
        rm = pyvisa.ResourceManager("@py")
        self.scope = rm.open_resource(address)
        self.scope.timeout = timeout_ms
        self.scope.chunk_size = 1 << 20  # 1 MB — faster waveform transfer
        idn = self.scope.query("*IDN?")
        if "SDS1104X-E" not in idn:
            raise RuntimeError(f"Unexpected scope: {idn!r}")

    def close(self) -> None:
        self.scope.close()

    def configure_channel(self, ch: int, vdiv: float, coupling: str = "DC",
                          offset: float = 0.0, probe: float = 1.0) -> None:
        self.scope.write(f"C{ch}:TRACE ON")
        self.scope.write(f"C{ch}:VOLT_DIV {vdiv}")
        self.scope.write(f"C{ch}:COUPLING {coupling}1M")
        self.scope.write(f"C{ch}:OFFSET {offset}")
        self.scope.write(f"C{ch}:ATTENUATION {probe}")

    def configure_timebase(self, tdiv: float) -> None:
        self.scope.write(f"TDIV {tdiv}")

    def configure_trigger(self, channel: int, level: float, slope: str = "POS") -> None:
        self.scope.write(f"TRIG_SELECT EDGE,SR,C{channel},HT,OFF")
        self.scope.write(f"C{channel}:TRIG_LEVEL {level}")
        self.scope.write(f"C{channel}:TRIG_SLOPE {slope}")

    def single_capture(self, channel: int, timeout_s: float = 5.0) -> np.ndarray:
        """Arm single trigger, wait for completion, return voltage samples."""
        self.scope.write("TRMD SINGLE")
        self.scope.write("ARM")
        t0 = time.time()
        while self.scope.query("SAST?").strip().endswith("Stop") is False:
            if time.time() - t0 > timeout_s:
                raise TimeoutError("Scope did not trigger in time")
            time.sleep(0.02)

        self.scope.write(f"C{channel}:WAVEFORM? DAT2")
        raw = self.scope.read_raw()

        # Siglent DAT2 format: "...#9NNNNNNNNN<data>\n\n"
        i = raw.find(b"#")
        header_len = int(raw[i + 1 : i + 2])
        data_len = int(raw[i + 2 : i + 2 + header_len])
        samples = np.frombuffer(
            raw[i + 2 + header_len : i + 2 + header_len + data_len], dtype=np.int8
        ).astype(np.float64)

        vdiv = float(self.scope.query(f"C{channel}:VDIV?").split()[-1])
        offset = float(self.scope.query(f"C{channel}:OFFSET?").split()[-1])
        # SDS1104X-E uses 25 codes per division
        return samples * (vdiv / 25.0) - offset
