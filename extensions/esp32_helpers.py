"""Copier scaffold-time loader for the canonical helper.

The actual implementation lives at
``template/[[project_name]]/tools/esp32_helpers.py`` so it lands inside
every scaffolded project for runtime use. This stub loads the same module
via filesystem path (Python cannot import a directory whose name contains
``[[`` and ``]]``) and exposes the Jinja2 Extension class that Copier
registers via ``_jinja_extensions`` in ``copier.yml``.

Single source of truth: edit only the file under ``template/...``. This
loader has no logic of its own beyond the import.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

from jinja2.ext import Extension

_REPO_ROOT = Path(__file__).resolve().parent.parent
_HELPER_PATH = _REPO_ROOT / "template" / "[[project_name]]" / "tools" / "esp32_helpers.py"

if not _HELPER_PATH.is_file():
    raise FileNotFoundError(
        f"Canonical esp32_helpers not found at {_HELPER_PATH}. "
        "The repo layout is broken; this stub expects the helper to live "
        "inside the template tree at template/[[project_name]]/tools/."
    )

_spec = importlib.util.spec_from_file_location("_esp32_helpers_canonical", _HELPER_PATH)
assert _spec is not None and _spec.loader is not None
_module = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_module)

parse_part_number = _module.parse_part_number
partition_layout = _module.partition_layout


class Esp32HelpersExtension(Extension):
    """Register ``parse_part_number`` and ``partition_layout`` on the Jinja env."""

    def __init__(self, environment):
        super().__init__(environment)
        environment.filters["parse_part_number"] = parse_part_number
        environment.globals["partition_layout"] = partition_layout
