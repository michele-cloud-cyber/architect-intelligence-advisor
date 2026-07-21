"""Contracts for evidence-based historical forecasting."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class MetricForecast:
    """One score forecast derived from an observed historical series."""

    metric: str
    current_score: float | None
    projected_score: float | None
    trend: str
    observations: int
    available: bool


@dataclass(frozen=True)
class ForecastReport:
    """Forecast output for all Dashboard V2 score dimensions."""

    forecasts: tuple[MetricForecast, ...]
