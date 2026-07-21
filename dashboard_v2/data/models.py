"""Backward-compatible re-export of application contracts for Dashboard V2."""

from sr.services.contracts import DashboardData, DashboardMetrics, TrendPoint

__all__ = ["DashboardData", "DashboardMetrics", "TrendPoint"]
