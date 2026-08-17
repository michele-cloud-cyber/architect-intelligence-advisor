"""V3 cross-cutting FinOps presentation interface."""

def render_finops() -> None:
    """Render a safe empty-state when no analyzed portfolio is available."""
    import streamlit as st
    from dashboard_v2.components.code_architecture import _render_finops
    bundle=st.session_state.get("v3_bundle")
    if bundle is None:
        st.info("FinOps Available · Analyze Terraform in Code & Test Lab to populate synthetic scenarios.")
        return
    _render_finops(bundle)
