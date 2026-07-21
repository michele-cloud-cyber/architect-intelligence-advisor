"""Stable application contracts consumed by presentation layers and future APIs."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any


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
class AssessmentSummary:
    """Compact metadata for the latest assessment, without changing snapshots."""

    last_assessment: datetime | None
    duration_seconds: float | None
    accounts_scanned: int | None
    regions_scanned: int | None


@dataclass(frozen=True)
class DashboardData:
    metrics: DashboardMetrics
    trend: tuple[TrendPoint, ...]
    risk_distribution: dict[str, int]
    source_label: str
    latest_scan_at: datetime | None
    assessment_summary: AssessmentSummary


@dataclass(frozen=True)
class CapabilityStatus:
    """Explicit contract for a future capability not implemented by V1 yet."""

    capability: str
    available: bool
    message: str


@dataclass(frozen=True)
class DashboardFilters:
    """Presentation-neutral scope selection for dashboard data."""

    organization: str | None = None
    account: str | None = None
    region: str | None = None


@dataclass(frozen=True)
class DashboardFilterOptions:
    organizations: tuple[str, ...]
    accounts: tuple[str, ...]
    regions: tuple[str, ...]


@dataclass(frozen=True)
class DashboardView:
    """Single read model returned by the internal application API."""

    data: DashboardData | None
    timeline: tuple[Any, ...]
    fingerprint: Any
    forecast: Any
    filtered_snapshot_count: int
