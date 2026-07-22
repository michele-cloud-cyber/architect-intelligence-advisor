"""KPI card components."""

from __future__ import annotations

import streamlit as st

from dashboard_v2.data.models import DashboardMetrics


def render_kpi_cards(metrics: DashboardMetrics) -> None:
    """Render the four principal architecture indicators."""

    cards = (
        ("Overall Health", metrics.overall_health, "Architecture posture"),
        ("Risk Score", metrics.risk_score, "Lower is better"),
        ("FinOps Score", metrics.finops_score, "Cost governance"),
        ("Compliance Score", metrics.compliance_score, "Control coverage"),
    )
    for column, (label, value, help_text) in zip(st.columns(4), cards):
        with column:
            display_value = f"{value:.0f}/100" if value is not None else "—"
            st.metric(label, display_value, help=help_text, border=True)
            if value is None:
                st.caption("Available after multiple assessments")
