"""Professional, dependency-light Vega-Lite charts for Dashboard V2."""

from __future__ import annotations

import streamlit as st

from dashboard_v2.data.models import DashboardData


_PALETTE = ["#ef4444", "#f97316", "#facc15", "#22c55e"]


def render_posture_pie(data: DashboardData) -> None:
    healthy = round(data.metrics.overall_health, 1)
    values = [
        {"segment": "Healthy posture", "value": healthy},
        {"segment": "Improvement area", "value": round(100 - healthy, 1)},
    ]
    spec = {
        "mark": {"type": "arc", "innerRadius": 62, "cornerRadius": 5},
        "encoding": {
            "theta": {"field": "value", "type": "quantitative"},
            "color": {
                "field": "segment",
                "type": "nominal",
                "scale": {"range": ["#38bdf8", "#334155"]},
                "legend": {"title": None, "orient": "bottom"},
            },
            "tooltip": [
                {"field": "segment", "type": "nominal", "title": "Area"},
                {"field": "value", "type": "quantitative", "title": "Score", "format": ".1f"},
            ],
        },
        "view": {"stroke": None},
    }
    st.vega_lite_chart(values, spec, use_container_width=True)


def render_trend_line(data: DashboardData) -> None:
    values = [
        {"date": point.timestamp.strftime("%Y-%m-%d"), "metric": "Overall Health", "score": point.overall_health}
        for point in data.trend
    ] + [
        {"date": point.timestamp.strftime("%Y-%m-%d"), "metric": "Risk Score", "score": point.risk_score}
        for point in data.trend
    ]
    spec = {
        "mark": {"type": "line", "point": {"filled": True, "size": 55}, "strokeWidth": 3},
        "encoding": {
            "x": {"field": "date", "type": "temporal", "title": None},
            "y": {"field": "score", "type": "quantitative", "title": "Score", "scale": {"domain": [0, 100]}},
            "color": {
                "field": "metric",
                "type": "nominal",
                "scale": {"domain": ["Overall Health", "Risk Score"], "range": ["#38bdf8", "#f97316"]},
                "legend": {"title": None, "orient": "bottom"},
            },
            "tooltip": [
                {"field": "date", "type": "temporal", "title": "Date"},
                {"field": "metric", "type": "nominal", "title": "Metric"},
                {"field": "score", "type": "quantitative", "title": "Score", "format": ".1f"},
            ],
        },
        "view": {"stroke": None},
    }
    st.vega_lite_chart(values, spec, use_container_width=True)


def render_risk_distribution(data: DashboardData) -> None:
    if sum(data.risk_distribution.values()) == 0:
        st.caption("No priority distribution is available in the selected V1 snapshot.")
        return

    values = [{"severity": key, "findings": value} for key, value in data.risk_distribution.items()]
    spec = {
        "mark": {"type": "bar", "cornerRadiusTopLeft": 5, "cornerRadiusTopRight": 5},
        "encoding": {
            "x": {
                "field": "severity",
                "type": "nominal",
                "sort": ["Critical", "High", "Medium", "Low"],
                "title": None,
            },
            "y": {"field": "findings", "type": "quantitative", "title": "Findings"},
            "color": {
                "field": "severity",
                "type": "nominal",
                "scale": {"domain": ["Critical", "High", "Medium", "Low"], "range": _PALETTE},
                "legend": None,
            },
            "tooltip": [
                {"field": "severity", "type": "nominal", "title": "Severity"},
                {"field": "findings", "type": "quantitative", "title": "Findings"},
            ],
        },
        "view": {"stroke": None},
    }
    st.vega_lite_chart(values, spec, use_container_width=True)
