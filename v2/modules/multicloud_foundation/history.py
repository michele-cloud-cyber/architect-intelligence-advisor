"""Local immutable scenario history with caller-supplied storage."""

from __future__ import annotations

from dataclasses import asdict
from .models import ScenarioSnapshot


class LocalScenarioHistory:
    def __init__(self):
        self._snapshots: dict[str, ScenarioSnapshot] = {}

    def append(self, snapshot: ScenarioSnapshot) -> None:
        if snapshot.scenario_id in self._snapshots:
            raise ValueError("Scenario snapshots are immutable")
        self._snapshots[snapshot.scenario_id] = snapshot

    def list(self) -> tuple[ScenarioSnapshot, ...]:
        return tuple(self._snapshots.values())

    def compare(self, left_id: str, right_id: str) -> dict:
        left, right = self._snapshots[left_id], self._snapshots[right_id]
        keys = sorted(set(left.scores) | set(right.scores))
        return {key: {"before": left.scores.get(key), "after": right.scores.get(key), "delta": right.scores.get(key, 0) - left.scores.get(key, 0)} for key in keys}

    def export_safe(self) -> list[dict]:
        return [asdict(item) for item in self.list()]
