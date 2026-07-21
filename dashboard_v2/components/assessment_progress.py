"""Progress feedback for an explicit V1 Landing Zone assessment."""

from __future__ import annotations

import streamlit as st

from sr.services.dashboard_service import DashboardService


_V1_STAGES = (
    "Collect IAM",
    "Collect Organizations",
    "Collect Security Hub",
    "Collect GuardDuty",
    "Collect CloudTrail",
    "Collect Config",
    "Calculate Risk Score",
    "Generate Fingerprint",
    "Save Historical Snapshot",
    "Refresh Dashboard",
)


def run_assessment_with_progress(service: DashboardService) -> None:
    """Run one real V1 scan while keeping progress feedback inside the V2 UI.

    V1 owns the actual execution. The checklist is finalized only after the V1
    service returns successfully; Config is called out because V1 does not yet
    include an AWS Config collector.
    """

    with st.status("V1 Landing Zone assessment in progress", expanded=True) as status:
        progress = st.progress(5, text="Starting the existing V1 assessment pipeline...")
        for stage in _V1_STAGES:
            if stage == "Collect Config":
                st.write("• Collect Config — not available in the current V1 collector")
            else:
                st.write(f"• {stage}")

        service.run_assessment()

        progress.progress(100, text="Refreshing dashboard state...")
        for stage in _V1_STAGES:
            if stage == "Collect Config":
                st.write("– Collect Config — skipped (not implemented in V1)")
            else:
                st.write(f"✓ {stage}")
        status.update(label="Assessment completed successfully", state="complete", expanded=False)
