"""Standalone demo-only entry point for the safe Windows package."""

import streamlit as st

from dashboard_v2.components.multicloud_foundation import render_multicloud_platform


st.set_page_config(
    page_title="Adaptive Multi-Cloud Landing Zone Orchestrator",
    page_icon="🧭",
    layout="wide",
)
st.markdown(
    """
    <style>
    .stApp { background: #0b1420; }
    [data-testid="stSidebar"] { background: #101c2b; border-right: 1px solid #25374d; }
    [data-testid="stMetric"] { background: #111f30; border: 1px solid #2a415b;
      border-radius: 12px; padding: 14px; }
    </style>
    """,
    unsafe_allow_html=True,
)

with st.sidebar:
    st.header("Architect Advisor")
    st.success("LOCAL DEMO / DEMO LOCALE · NO AWS CONNECTION")

render_multicloud_platform()
