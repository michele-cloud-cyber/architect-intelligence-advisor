"""Streamlit presentation component for real Landing Zone timeline events."""

from __future__ import annotations

import streamlit as st

from v2.modules.landing_zone_timeline.models import TimelineEvent


_SEVERITY_ICON = {"High": "🔴", "Medium": "🟠", "Info": "🔵"}
_EVENT_ICON = {
    "Assessment": "🧭",
    "Fingerprint": "🔐",
    "Finding": "🔎",
    "Risk Score": "⚠️",
    "Overall Health": "🛡️",
    "Forecast": "📈",
}


def render_timeline(events: list[TimelineEvent] | tuple[TimelineEvent, ...]) -> None:
    """Render a compact timeline with an explicit expand/collapse control."""

    st.subheader("Landing Zone Timeline")
    st.caption("Changes detected by comparing consecutive assessment snapshots.")
    if not events:
        st.info("At least one valid history snapshot is required to display the timeline.")
        return

    expanded = st.session_state.get("timeline_expanded", False)
    if len(events) > 5:
        label = "⌃ Collapse history" if expanded else "⌄ Show full history"
        if st.button(label, key="timeline_expand", use_container_width=True):
            st.session_state["timeline_expanded"] = not expanded
            expanded = not expanded

    visible_events = events if expanded else events[:5]
    st.caption(f"Mostrati {len(visible_events)} di {len(events)} eventi")

    for event in visible_events:
        icon = _EVENT_ICON.get(event.category, "📌")
        severity_icon = _SEVERITY_ICON.get(event.severity, "⚪")
        with st.container(border=True):
            date, category = st.columns([1, 4])
            with date:
                st.caption(event.timestamp.strftime("%d %b %Y\n%H:%M"))
            with category:
                st.markdown(f"{icon} **{event.category}** {severity_icon}")
                st.write(event.summary)
