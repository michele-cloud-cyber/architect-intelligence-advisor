"""Layout primitives and visual framing for Dashboard V2."""

from __future__ import annotations

from datetime import datetime

import streamlit as st


def configure_page() -> None:
    st.set_page_config(page_title="Architect Advisor V2", page_icon="🧭", layout="wide")


def render_header(source_label: str, latest_scan_at: datetime | None) -> None:
    st.title("🧭 Architect Advisor — Version 2")
    st.caption("AWS Landing Zone decision intelligence workspace")
    scan_label = latest_scan_at.strftime("%d %b %Y, %H:%M") if latest_scan_at else "No scan available"
    left, right = st.columns([3, 1])
    with left:
        st.caption(f"Source: {source_label}")
    with right:
        st.caption(f"Latest scan: {scan_label}")
    st.divider()


def render_sidebar() -> bool:
    with st.sidebar:
        st.header("Dashboard V2")
        st.caption("Consumes V1 data without changing V1 code.")
        st.selectbox("Scope", ["Organization", "Production", "Shared Services"], disabled=True)
        st.selectbox("Region", ["All regions"], disabled=True)
        st.info("Scope filters will be connected to future V2 modules.")
        return st.button("Run V1 assessment", type="primary", use_container_width=True)
