"""sigrok-cli subprocess wrapper for digital capture and protocol decode."""

import csv
import subprocess
from pathlib import Path


class SigrokLA:
    """
    Thin wrapper around sigrok-cli.
    System requirement: sudo apt install sigrok-cli  (or brew install sigrok)

    Configure via env vars set in conftest.py:
      SIGROK_DRIVER  — sigrok driver name (default: fx2lafw for FX2-based analysers)
      SIGROK_CONN    — connection string, e.g. "1.5" for USB bus.device (optional)

    Run `sigrok-cli --list-supported` to see all drivers and protocol decoders.
    """

    def __init__(
        self,
        driver: str = "fx2lafw",
        conn: str | None = None,
        sample_rate: int = 4_000_000,
    ) -> None:
        self.driver = driver
        self.conn = conn
        self.sample_rate = sample_rate

    def _base_cmd(self) -> list[str]:
        cmd = ["sigrok-cli", f"--driver={self.driver}"]
        if self.conn:
            cmd += [f"--conn={self.conn}"]
        return cmd

    def capture(
        self,
        channels: list[str],
        duration_s: float,
        output_path: Path | None = None,
    ) -> dict[str, list[int]]:
        """Capture digital samples. Returns {channel_name: [0/1, ...]}."""
        n_samples = int(self.sample_rate * duration_s)
        out = output_path or Path("/tmp/_sigrok_capture.csv")
        subprocess.run(
            self._base_cmd()
            + [
                f"--channels={','.join(channels)}",
                f"--config=samplerate={self.sample_rate}",
                f"--samples={n_samples}",
                "--output-format=csv",
                f"--output-file={out}",
            ],
            check=True,
            capture_output=True,
        )
        result: dict[str, list[int]] = {ch: [] for ch in channels}
        with open(out) as f:
            for row in csv.reader(f):
                if not row or row[0].startswith(";"):
                    continue
                for i, ch in enumerate(channels):
                    result[ch].append(int(row[i]))
        return result

    def decode(
        self,
        protocol: str,
        channel_map: dict[str, str],
        duration_s: float,
    ) -> list[str]:
        """
        Run a protocol decoder. Returns annotation lines from stdout.

        channel_map maps PD pin names to LA channel names:
          {"scl": "D0", "sda": "D1"}  ->  i2c:scl=D0:sda=D1

        See `sigrok-cli --list-supported` for available protocol decoders and pin names.
        """
        n_samples = int(self.sample_rate * duration_s)
        pd_arg = protocol + ":" + ":".join(
            f"{pin}={ch}" for pin, ch in channel_map.items()
        )
        proc = subprocess.run(
            self._base_cmd()
            + [
                f"--channels={','.join(channel_map.values())}",
                f"--config=samplerate={self.sample_rate}",
                f"--samples={n_samples}",
                f"--protocol-decoders={pd_arg}",
                "--output-format=ascii",
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        return proc.stdout.splitlines()
