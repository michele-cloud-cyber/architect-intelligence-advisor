"""Stable application contracts consumed by presentation layers and future APIs."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class TrendPoint:
    timestamp: datetime
    overall_health: float
    risk_score: float


@dataclass(frozen=True)
class DashboardMetrics:
    overall_health: float
    risk_score: float
    finops_score: float | None
    compliance_score: float | None


@dataclass(frozen=True)
class DashboardData:
    metrics: DashboardMetrics
    trend: tuple[TrendPoint, ...]
    risk_distribution: dict[str, int]
    source_label: str
    latest_scan_at: datetime | None


@dataclass(frozen=True)
class CapabilityStatus:
    """Explicit contract for a future capability not implemented by V1 yet."""

    capability: str
    available: bool
    message: str
