"""Standalone demo-only entry point for the safe Windows package."""

import streamlit as st

from dashboard_v2.components.platform_lab import render_platform_lab


st.set_page_config(
    page_title="AWS Interactive Architecture Lab",
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

render_platform_lab()
