"""Layout primitives and visual framing for Dashboard V2."""

from __future__ import annotations

from datetime import datetime

import streamlit as st

from sr.services.contracts import AssessmentSummary, DashboardFilterOptions, DashboardFilters


def configure_page() -> None:
    st.set_page_config(page_title="Architect Advisor", page_icon="🧭", layout="wide")
    st.markdown(
        """
        <style>
        .stApp { background: #0b1420; }
        [data-testid="stSidebar"] { background: #101c2b; border-right: 1px solid #25374d; }
        [data-testid="stMetric"] { background: #111f30; border: 1px solid #2a415b; border-radius: 12px;
          padding: 14px; animation: aa-fade-slide .28s ease-out; }
        [data-testid="stMetricValue"] { color: #e8f1fb; }
        [data-testid="stVerticalBlockBorderWrapper"] { border-color: #2a415b; border-radius: 12px; }
        .aa-enter { animation: aa-fade-slide .25s ease-out; }
        @keyframes aa-fade-slide { from { opacity: 0; transform: translateY(5px); }
          to { opacity: 1; transform: translateY(0); } }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_header(source_label: str, latest_scan_at: datetime | None, summary: AssessmentSummary) -> None:
    st.title("🧭 Architect Advisor — Version 2")
    st.caption("AWS Landing Zone decision intelligence workspace")
    scan_label = latest_scan_at.strftime("%d %b %Y, %H:%M") if latest_scan_at else "No scan available"
    left, right = st.columns([3, 1])
    with left:
        st.caption(f"Source: {source_label}")
    with right:
        st.caption(f"Latest scan: {scan_label}")
    summary_columns = st.columns(4)
    _summary_metric(summary_columns[0], "Last Assessment", scan_label)
    _summary_metric(summary_columns[1], "Assessment Duration", _duration_label(summary.duration_seconds))
    _summary_metric(summary_columns[2], "Accounts Scanned", _count_label(summary.accounts_scanned))
    _summary_metric(summary_columns[3], "Regions Scanned", _count_label(summary.regions_scanned))
    st.divider()


def render_sidebar(options: DashboardFilterOptions) -> tuple[DashboardFilters, bool]:
    with st.sidebar:
        st.header("Architect Advisor")
        st.caption("Enterprise Landing Zone Intelligence")
        st.markdown("### Scope")
        organization_options = ["All organizations", *options.organizations] or ["No Organizations found"]
        account_options = ["All accounts", *options.accounts] or ["No Accounts found"]
        region_options = ["All regions", *options.regions] or ["No Regions available"]
        organization = st.selectbox("Organization", organization_options, key="filter_organization")
        account = st.selectbox("AWS Account", account_options, key="filter_account")
        region = st.selectbox("AWS Region", region_options, key="filter_region")
        if not options.organizations:
            st.caption("No Organizations found · Connect AWS first")
        if not options.accounts:
            st.caption("No Accounts found · Connect AWS first")
        if not options.regions:
            st.caption("No Regions available · Connect AWS first")
        st.caption("Filters scope the historical snapshots displayed in the dashboard.")
        st.divider()
        run_assessment = st.button("Start Assessment", type="primary", use_container_width=True)
        return (
            DashboardFilters(
                organization=organization if organization in options.organizations else None,
                account=account if account in options.accounts else None,
                region=region if region in options.regions else None,
            ),
            run_assessment,
        )


def _summary_metric(column, label: str, value: str) -> None:
    with column:
        st.caption(label)
        st.markdown(f"**{value}**")


def _duration_label(value: float | None) -> str:
    return f"{value:.1f}s" if value is not None else "—"


def _count_label(value: int | None) -> str:
    return str(value) if value is not None else "—"
