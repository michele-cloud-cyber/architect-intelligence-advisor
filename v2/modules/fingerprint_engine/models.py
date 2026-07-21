"""Contracts for V2 fingerprint reporting."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class FingerprintChange:
    """One measurable difference between two V1-generated fingerprints."""

    dimension: str
    previous: str
    current: str


@dataclass(frozen=True)
class FingerprintReport:
    """Current V1 fingerprint plus its latest historical comparison."""

    timestamp: datetime
    architecture: str | None
    overall_score: float | None
    hash_value: str | None
    changes: tuple[FingerprintChange, ...]
