"""Presentation component for historical score forecasts."""

from __future__ import annotations

import streamlit as st

from v2.modules.forecast_engine.models import ForecastReport


def render_forecast(report: ForecastReport) -> None:
    """Render evidence-based forecast cards without placeholder score values."""

    st.subheader("Forecast Engine")
    st.caption("Projection for the next assessment, calculated from the available historical trend.")

    confidence = _prediction_confidence(report)
    columns = st.columns(len(report.forecasts) + 1)
    for column, forecast in zip(columns, report.forecasts):
        with column:
            if not forecast.available:
                st.metric(forecast.metric, "N/A", help="At least two real observations are required.", border=True)
                st.caption("Insufficient historical data")
                continue
            delta = forecast.projected_score - forecast.current_score
            st.metric(
                forecast.metric,
                f"{forecast.projected_score:.1f}/100",
                delta=f"{delta:+.1f} vs current",
                delta_color="inverse" if forecast.metric == "Risk Score" else "normal",
                border=True,
            )
            st.caption(f"{forecast.trend} · {forecast.observations} observations")

    with columns[-1]:
        st.metric("Prediction Confidence", f"{confidence}%", help="Derived from available historical observations.", border=True)
        st.caption("Historical coverage")


def _prediction_confidence(report: ForecastReport) -> int:
    """Estimate confidence from real history coverage without changing Forecast V1."""

    available = [item for item in report.forecasts if item.available]
    observations = max((item.observations for item in available), default=0)
    return min(92, max(25, 42 + min(observations, 10) * 4 + len(available) * 5))
