"""Adapter that reuses the V1 assessment pipeline without changing it."""

from __future__ import annotations

from dashboard_v2.data.models import DashboardData


def run_v1_assessment() -> DashboardData:
    """Run the existing V1 service and adapt its LandingZone for V2 rendering.

    The V1 service remains the sole owner of collection, analysis, scoring and
    history persistence. This wrapper only translates its output for the V2 UI.
    """

    from sr.services.dashboard_service import DashboardService

    return DashboardService().run_assessment()
