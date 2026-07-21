"""Read-only adapter for V1 history snapshots and future V2 snapshots."""

from __future__ import annotations

from pathlib import Path

from dashboard_v2.data.models import DashboardData
from sr.services.dashboard_service import DashboardService


def load_dashboard_data(project_root: Path) -> DashboardData | None:
    """Load normalized dashboard data without creating or changing history files."""

    return DashboardService(project_root).get_dashboard_data()


def dashboard_data_from_snapshots(snapshots) -> DashboardData:
    """Normalize V1-compatible snapshots into the V2 presentation contract."""

    return DashboardService().dashboard_data_from_snapshots(snapshots)


def load_history_snapshots(project_root: Path):
    """Return valid V1/V2 snapshots from the project history directory, oldest first."""

    return DashboardService(project_root).get_history()
