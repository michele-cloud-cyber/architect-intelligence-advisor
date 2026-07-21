"""Forecast score evolution from persisted V1/V2 snapshot history."""

from __future__ import annotations

from typing import Any, Callable, Iterable

from v2.modules.forecast_engine.models import ForecastReport, MetricForecast


MetricExtractor = Callable[[dict[str, Any]], float | None]


def build_forecast_report(snapshots: Iterable[dict[str, Any]]) -> ForecastReport:
    """Project the next observed score using a least-squares historical trend.

    No score is invented when V1/V2 history does not expose that metric. The
    existing V1 ForecastEngine remains unchanged and can continue to persist its
    qualitative ``forecast`` field alongside these historical projections.
    """

    ordered = list(snapshots)
    forecasts = tuple(
        _forecast_metric(name, extractor, lower_is_better, ordered)
        for name, extractor, lower_is_better in _METRICS
    )
    return ForecastReport(forecasts=forecasts)


def _forecast_metric(
    name: str,
    extractor: MetricExtractor,
    lower_is_better: bool,
    snapshots: list[dict[str, Any]],
) -> MetricForecast:
    values = [value for snapshot in snapshots if (value := extractor(snapshot)) is not None]
    if len(values) < 2:
        return MetricForecast(name, values[-1] if values else None, None, "Insufficient data", len(values), False)

    slope = _least_squares_slope(values)
    current = values[-1]
    projected = _clamp(current + slope)
    trend = _trend_label(slope, lower_is_better)
    return MetricForecast(name, current, projected, trend, len(values), True)


def _least_squares_slope(values: list[float]) -> float:
    count = len(values)
    mean_x = (count - 1) / 2
    mean_y = sum(values) / count
    numerator = sum((index - mean_x) * (value - mean_y) for index, value in enumerate(values))
    denominator = sum((index - mean_x) ** 2 for index in range(count))
    return numerator / denominator if denominator else 0.0


def _trend_label(slope: float, lower_is_better: bool) -> str:
    if abs(slope) < 0.25:
        return "Stable"
    improving = slope < 0 if lower_is_better else slope > 0
    return "Improving" if improving else "Worsening"


def _risk_score(snapshot: dict[str, Any]) -> float | None:
    value = snapshot.get("risk_score")
    if isinstance(value, dict):
        value = value.get("score")
    return _numeric(value)


def _security_score(snapshot: dict[str, Any]) -> float | None:
    value = snapshot.get("security_score")
    if value is None and isinstance(snapshot.get("fingerprint"), dict):
        value = snapshot["fingerprint"].get("security")
    return _numeric(value)


def _numeric(value: Any) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _clamp(value: float) -> float:
    return max(0.0, min(100.0, value))


_METRICS: tuple[tuple[str, MetricExtractor, bool], ...] = (
    ("Risk Score", _risk_score, True),
    ("Security", _security_score, False),
    ("FinOps", lambda snapshot: _numeric(snapshot.get("finops_score")), False),
    ("Compliance", lambda snapshot: _numeric(snapshot.get("compliance_score")), False),
)
