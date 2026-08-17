"""The only state contract shared by unified sections."""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from typing import Any


STATE_SCHEMA_VERSION = "1.0"


@dataclass(frozen=True)
class NormalizedAppState:
    schema_version: str = STATE_SCHEMA_VERSION
    active_view: str = "Vista completa"
    operating_mode: str = "Demo"
    selected_providers: tuple[str, ...] = ("AWS", "Azure", "GCP")
    selected_scenario_id: str | None = None
    context: dict[str, Any] = field(default_factory=dict)

    def evolve(self, **changes: Any) -> "NormalizedAppState":
        candidate = replace(self, **changes)
        if candidate.schema_version != STATE_SCHEMA_VERSION:
            raise ValueError("Unsupported shared-state schema version")
        if candidate.operating_mode not in {"Demo", "Simulation", "Read-only"}:
            raise ValueError("Unsupported operating mode")
        return candidate
