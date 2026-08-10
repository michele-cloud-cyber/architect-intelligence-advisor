"""Independent Streamlit entry point for Architect Advisor Dashboard V2."""

from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from dashboard_v2.components.charts import (  # noqa: E402
    render_posture_pie,
    render_risk_distribution,
    render_trend_line,
)
from dashboard_v2.components.assessment_progress import run_assessment_with_progress  # noqa: E402
from dashboard_v2.components.ai_storytelling import render_ai_storytelling  # noqa: E402
from dashboard_v2.components.fingerprint import render_fingerprint  # noqa: E402
from dashboard_v2.components.forecast import render_forecast  # noqa: E402
from dashboard_v2.components.kpi_cards import render_kpi_cards  # noqa: E402
from dashboard_v2.components.layout import configure_page, render_header, render_sidebar  # noqa: E402
from dashboard_v2.components.security_findings import render_security_findings  # noqa: E402
from dashboard_v2.components.timeline import render_timeline  # noqa: E402
from dashboard_v2.components.platform_lab import render_platform_lab  # noqa: E402
from sr.services.dashboard_service import DashboardService  # noqa: E402


configure_page()

workspace = st.sidebar.radio(
    "Workspace",
    ["Advisor Dashboard", "Interactive AWS Lab"],
    index=1,
    key="workspace_navigation",
)

if workspace == "Interactive AWS Lab":
    render_platform_lab()
    st.stop()

if "dashboard_service" not in st.session_state:
    st.session_state["dashboard_service"] = DashboardService(PROJECT_ROOT)
service = st.session_state["dashboard_service"]
filters, run_assessment = render_sidebar(service.get_filter_options())

if run_assessment:
    run_assessment_with_progress(service)
    st.session_state["assessment_completed"] = True

view = service.get_dashboard_view(filters)
data = view.data

if data is None:
    st.title("Architect Advisor — Version 2")
    st.info(
        "No V1 assessment history is available yet. Run a V1 assessment from the sidebar "
        "to collect real data using the existing V1 pipeline."
    )
    st.stop()

if st.session_state.pop("assessment_completed", False):
    st.success("Assessment completed successfully")

render_header(data.source_label, data.latest_scan_at, data.assessment_summary)
st.caption(f"Selected scope contains {view.filtered_snapshot_count} historical snapshots.")

render_kpi_cards(data.metrics)
st.divider()

posture_column, risk_column = st.columns(2)
with posture_column:
    with st.container(border=True):
        st.subheader("Overall posture")
        st.caption("Healthy posture versus improvement area")
        render_posture_pie(data)

with risk_column:
    with st.container(border=True):
        st.subheader("Risk distribution")
        st.caption("Open recommendations grouped by severity")
        render_risk_distribution(data)

with st.container(border=True):
    st.subheader("Historical posture trend")
    st.caption("Scores are loaded from compatible V1 or future V2 history snapshots.")
    render_trend_line(data)

st.divider()
render_timeline(view.timeline)

st.divider()
render_fingerprint(view.fingerprint)

st.divider()
render_forecast(view.forecast)

st.divider()
render_ai_storytelling(
    service.get_ai_storytelling_status(filters),
    lambda: service.generate_demo_storytelling(filters),
    lambda: service.generate_ai_storytelling(filters),
)

st.divider()
render_security_findings(service.get_demo_security_case())

st.info("The dashboard uses existing V1 assessment outputs. FinOps and Compliance are available after multiple assessments.")
