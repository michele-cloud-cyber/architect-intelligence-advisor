"""On-demand Bedrock storytelling panel for historical assessments."""

from __future__ import annotations

from collections.abc import Callable

import streamlit as st

from sr.services.contracts import CapabilityStatus


def render_ai_storytelling(status: CapabilityStatus, generate_story: Callable[[], str]) -> None:
    """Render an explicit, opt-in Bedrock action over real historical data."""

    st.subheader("AI Storytelling")
    st.caption("Bedrock compares the two latest real snapshots; no demo context is used.")

    if not status.available:
        st.info(status.message)
        return

    if st.button("Generate historical narrative", type="primary", key="generate_ai_story"):
        try:
            with st.spinner("Comparing historical evidence with Bedrock..."):
                st.session_state["v2_ai_story"] = generate_story()
        except Exception as error:
            st.error(f"Bedrock storytelling unavailable: {error}")

    story = st.session_state.get("v2_ai_story")
    if story:
        with st.container(border=True):
            st.markdown(story)
