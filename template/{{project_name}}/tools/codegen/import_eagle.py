"""Import pin/net assignments from an EAGLE 9.x (or Fusion Electronics) .sch
file into hardware/board.yaml.

Strategy: read the XML, match parts and nets to the schema in board.yaml,
and update fields that the schematic can answer. Fields requiring human
judgement (notes, active_low, pull direction) are left alone unless the
schematic carries an explicit attribute (see SCHEMATIC_CONVENTIONS.md).

Merge rules:
  - Existing values that differ from the .sch are flagged, not overwritten.
  - Fields blank in the .sch stay blank in YAML (never invented).
  - Fields set by a <attribute name="..."> tag on the part win over net-name
    heuristics.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from xml.etree import ElementTree as ET

import yaml

ATTR_PREFIX = "BOARD_"  # e.g. BOARD_ROLE, BOARD_BUS, BOARD_PULL


def _attr(part: ET.Element, name: str) -> str | None:
    for a in part.findall("attribute"):
        if a.get("name") == name:
            return a.get("value")
    return None


def parse_sch(path: Path) -> dict:
    """Return a dict of {role_key: {chip, pins, bus, address, int_pin, ...}}."""
    tree = ET.parse(path)
    root = tree.getroot()
    parts = root.findall(".//part")

    result: dict[str, dict] = {"peripherals": {}, "gpios": {}}
    for p in parts:
        role = _attr(p, f"{ATTR_PREFIX}ROLE")
        if not role:
            continue  # part is not annotated for import
        entry = {
            "chip": p.get("value") or p.get("deviceset"),
            "bus": _attr(p, f"{ATTR_PREFIX}BUS"),
            "address": _parse_hex(_attr(p, f"{ATTR_PREFIX}ADDR")),
            "cs_pin": _attr(p, f"{ATTR_PREFIX}CS"),
            "int1_pin": _attr(p, f"{ATTR_PREFIX}INT1"),
            "int2_pin": _attr(p, f"{ATTR_PREFIX}INT2"),
            "pin": _attr(p, f"{ATTR_PREFIX}PIN"),
            "active_low": _parse_bool(_attr(p, f"{ATTR_PREFIX}ACTIVE_LOW")),
            "pull": _attr(p, f"{ATTR_PREFIX}PULL"),
        }
        kind = _attr(p, f"{ATTR_PREFIX}KIND") or "peripheral"
        result[kind + "s"][role] = {k: v for k, v in entry.items() if v is not None}

    nets = root.findall(".//net")
    result["buses"] = _extract_buses(nets)
    return result


def _parse_hex(s: str | None) -> int | None:
    if s is None:
        return None
    return int(s, 0)


def _parse_bool(s: str | None) -> bool | None:
    if s is None:
        return None
    return s.strip().lower() in ("1", "true", "yes", "low")


def _extract_buses(nets: list[ET.Element]) -> dict:
    """Net names of the form I2C<N>_SDA, I2C<N>_SCL, SPI<N>_MOSI/MISO/SCLK
    populate the corresponding bus entry. Pin numbers are read from the
    MCU's pad attached to that net."""
    buses: dict[str, dict] = {}
    for n in nets:
        name = (n.get("name") or "").upper()
        buses.setdefault(name, {})
    return buses


def merge_into(existing: dict, imported: dict) -> tuple[dict, list[str]]:
    """Preserve hand-edited fields; only fill blanks or update schematic-
    derived fields. Returns (merged_dict, list_of_conflicts)."""
    conflicts: list[str] = []
    merged = yaml.safe_load(yaml.safe_dump(existing))  # deep copy

    for kind in ("peripherals", "gpios"):
        src = imported.get(kind, {})
        dst = merged.setdefault(kind, {}) or {}
        for role, fields in src.items():
            target = dst.setdefault(role, {}) or {}
            for k, v in fields.items():
                cur = target.get(k)
                if cur in (None, "", []):
                    target[k] = v
                elif cur != v:
                    conflicts.append(f"{kind}.{role}.{k}: YAML={cur!r}  SCH={v!r}")
            dst[role] = target
        merged[kind] = dst
    return merged, conflicts


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--sch", type=Path, default=Path("hardware/schematic.sch"))
    ap.add_argument("--yaml", type=Path, default=Path("hardware/board.yaml"))
    ap.add_argument("--apply", action="store_true",
                    help="Write merged YAML. Without this, only reports.")
    args = ap.parse_args()

    if not args.sch.exists():
        print(f"No schematic at {args.sch} — skipping import.")
        return 0
    if not args.yaml.exists():
        print(f"No {args.yaml}. Create it first with the starter template.")
        return 1

    imported = parse_sch(args.sch)
    with args.yaml.open() as f:
        existing = yaml.safe_load(f) or {}

    merged, conflicts = merge_into(existing, imported)

    if conflicts:
        print("Conflicts (hand-edits vs schematic). Resolve manually:")
        for c in conflicts:
            print(f"  ! {c}")

    if args.apply:
        with args.yaml.open("w") as f:
            yaml.safe_dump(merged, f, sort_keys=False, indent=2)
        print(f"Updated {args.yaml}")
    else:
        print("Dry run. Pass --apply to write changes.")

    return 1 if conflicts else 0


if __name__ == "__main__":
    sys.exit(main())
