"""Nordic Power Profiler Kit II wrapper.

Two modes:
  - Source Meter: PPK2 powers the DUT (use for sleep-current tests).
  - Ampere Meter: PPK2 sits in series with an external supply (easier wiring).
"""
from __future__ import annotations

import time

import numpy as np
from ppk2_api.ppk2_api import PPK2_API


class PPK2:
    def __init__(self, port: str):
        self.ppk = PPK2_API(port)
        self.ppk.get_modifiers()

    def source_mode(self, voltage_mv: int) -> None:
        self.ppk.use_source_meter()
        self.ppk.set_source_voltage(voltage_mv)
        self.ppk.toggle_DUT_power("ON")

    def ampere_mode(self) -> None:
        self.ppk.use_ampere_meter()

    def capture(self, duration_s: float) -> np.ndarray:
        """Return current samples in microamps over the requested duration."""
        self.ppk.start_measuring()
        end = time.time() + duration_s
        buf = bytearray()
        while time.time() < end:
            data = self.ppk.get_data()
            if data:
                buf.extend(data)
            time.sleep(0.01)
        self.ppk.stop_measuring()
        samples, _ = self.ppk.get_samples(bytes(buf))
        return np.asarray(samples, dtype=np.float64)

    def close(self) -> None:
        try:
            self.ppk.toggle_DUT_power("OFF")
        except Exception:
            pass
