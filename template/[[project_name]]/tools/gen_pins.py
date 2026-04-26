"""Generate components/board/include/board/Pins.hpp from hardware/board.yaml.

Strict mode (--check): exits non-zero if the generated file differs from
what's currently on disk. Pre-commit uses this to reject stale headers.
"""
from __future__ import annotations

import argparse
import hashlib
import re
import sys
from pathlib import Path

import yaml

HEADER = """\
// AUTO-GENERATED from hardware/board.yaml
// Do not edit by hand — edit the YAML and run `uv run gen-pins`.
// yaml-sha256: {sha}

#pragma once
#include <cstdint>

namespace board {{

"""

FOOTER = """
}}  // namespace board
"""


def _gpio_to_int(v: str | int | None) -> int | None:
    if v is None or v == "":
        return None
    if isinstance(v, int):
        return v
    m = re.fullmatch(r"GPIO(\d+)", v.strip(), flags=re.IGNORECASE)
    if not m:
        raise ValueError(f"Not a GPIO literal: {v!r}")
    return int(m.group(1))


def generate(yaml_path: Path) -> str:
    data = yaml.safe_load(yaml_path.read_text()) or {}
    sha = hashlib.sha256(yaml_path.read_bytes()).hexdigest()[:16]

    out = HEADER.format(sha=sha)

    # --- buses ---
    for bus_name, fields in (data.get("buses") or {}).items():
        up = bus_name.upper()
        for key in ("sda", "scl", "mosi", "miso", "sclk"):
            pin = _gpio_to_int(fields.get(key))
            if pin is not None:
                out += f"constexpr int {up}_{key.upper()}_PIN = {pin};\n"
        speed = fields.get("speed_hz")
        if speed:
            out += f"constexpr uint32_t {up}_SPEED_HZ = {speed};\n"
        out += "\n"

    # --- peripherals ---
    for role, fields in (data.get("peripherals") or {}).items():
        up = role.upper()
        addr = fields.get("address")
        if addr is not None:
            out += f"constexpr uint8_t {up}_I2C_ADDR = 0x{int(addr):02X};\n"
        for key in ("cs_pin", "int1_pin", "int2_pin"):
            pin = _gpio_to_int(fields.get(key))
            if pin is not None:
                out += f"constexpr int {up}_{key[:-4].upper()}_PIN = {pin};\n"
        out += "\n"

    # --- freestanding gpios ---
    for role, fields in (data.get("gpios") or {}).items():
        up = role.upper()
        pin = _gpio_to_int(fields.get("pin"))
        if pin is not None:
            out += f"constexpr int {up}_PIN = {pin};\n"
            al = fields.get("active_low")
            if al is not None:
                out += f"constexpr bool {up}_ACTIVE_LOW = {str(bool(al)).lower()};\n"
        out += "\n"

    out += FOOTER
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--yaml", type=Path, default=Path("hardware/board.yaml"))
    ap.add_argument("--out", type=Path,
                    default=Path("components/board/include/board/Pins.hpp"))
    ap.add_argument("--check", action="store_true",
                    help="Exit 1 if the generated content differs from --out.")
    args = ap.parse_args()

    content = generate(args.yaml)

    if args.check:
        current = args.out.read_text() if args.out.exists() else ""
        if current != content:
            print(f"❌ {args.out} is stale. Run: uv run gen-pins", file=sys.stderr)
            return 1
        return 0

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(content)
    print(f"Wrote {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
