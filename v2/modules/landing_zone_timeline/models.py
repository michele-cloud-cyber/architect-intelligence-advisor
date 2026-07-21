"""Domain contracts for the Landing Zone Timeline module."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class TimelineEvent:
    """A verifiable change detected between two assessment snapshots."""

    timestamp: datetime
    category: str
    summary: str
    severity: str = "Info"
