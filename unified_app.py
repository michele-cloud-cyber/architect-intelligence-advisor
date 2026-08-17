"""Third, independent Streamlit entry point for the complete modular view."""

import streamlit as st

from dashboard_v2.components.unified_shell import render_unified_application


st.set_page_config(page_title="Architect Advisor · Vista completa", page_icon="🧭", layout="wide")
st.markdown("""
<style>
.stApp { background: #0b1420; }
[data-testid="stSidebar"] { background: #101c2b; border-right: 1px solid #25374d; }
[data-testid="stMetric"] { background: #111f30; border: 1px solid #2a415b; border-radius: 12px; padding: 14px; }
</style>
""", unsafe_allow_html=True)
render_unified_application()
