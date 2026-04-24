"""Serial command interface to the DUT.

The firmware should expose a simple line-based command REPL under a
DEBUG_CMDS Kconfig option. Examples:
    > set_pwm_duty 50
    OK
    > read_adc 0
    1823
"""
from __future__ import annotations

import serial


class DUT:
    def __init__(self, port: str, baud: int = 115200, timeout_s: float = 1.0):
        self.ser = serial.Serial(port, baud, timeout=timeout_s)
        self.ser.reset_input_buffer()

    def send(self, cmd: str) -> str:
        self.ser.write((cmd.strip() + "\n").encode())
        self.ser.flush()
        return self.ser.readline().decode(errors="replace").strip()

    def expect_ok(self, cmd: str) -> None:
        reply = self.send(cmd)
        if reply != "OK":
            raise RuntimeError(f"{cmd!r} -> {reply!r}")

    def drain_logs(self, until_pattern: str, timeout_s: float = 5.0) -> list[str]:
        """Read serial output until a line matches `until_pattern` or timeout."""
        import re
        import time
        pattern = re.compile(until_pattern)
        deadline = time.time() + timeout_s
        lines: list[str] = []
        while time.time() < deadline:
            line = self.ser.readline().decode(errors="replace").rstrip()
            if not line:
                continue
            lines.append(line)
            if pattern.search(line):
                return lines
        raise TimeoutError(f"Pattern {until_pattern!r} not seen within {timeout_s}s; got {lines!r}")

    def close(self) -> None:
        self.ser.close()
