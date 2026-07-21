"""Streamlit presentation component for real Landing Zone timeline events."""

from __future__ import annotations

import streamlit as st

from v2.modules.landing_zone_timeline.models import TimelineEvent


_SEVERITY_ICON = {"High": "🔴", "Medium": "🟠", "Info": "🔵"}


def render_timeline(events: list[TimelineEvent]) -> None:
    """Render a chronological timeline without manufacturing missing events."""

    st.subheader("Landing Zone Timeline")
    st.caption("Changes detected by comparing consecutive assessment snapshots.")
    if not events:
        st.info("At least one valid history snapshot is required to display the timeline.")
        return

    for event in events:
        icon = _SEVERITY_ICON.get(event.severity, "⚪")
        with st.container(border=True):
            date, category = st.columns([1, 4])
            with date:
                st.caption(event.timestamp.strftime("%d %b %Y\n%H:%M"))
            with category:
                st.markdown(f"{icon} **{event.category}**")
                st.write(event.summary)
