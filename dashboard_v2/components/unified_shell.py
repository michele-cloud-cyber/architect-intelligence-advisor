"""Complete modular view with per-section failure isolation."""

from __future__ import annotations

from collections.abc import Callable
import traceback

import streamlit as st

from dashboard_v2.components.multicloud_foundation import (
    foundation_runtime, render_governance_plane, render_multicloud_overview,
    render_multicloud_platform, render_scenario_history,
)
from dashboard_v2.components.platform_lab import render_platform_lab
from v2.modules.unified_shell import HealthStatus, NormalizedAppState, probe_modules


STABLE_COMMIT = "7e1db43"
FOUNDATION_COMMIT = "45722f1"
UNIFIED_VERSION = "2.1-unified"


def _safe_section(title: str, renderer: Callable[[], None], module_id: str, forced_failure: str | None) -> None:
    st.subheader(title)
    try:
        if forced_failure == module_id:
            raise RuntimeError("Guasto diagnostico simulato")
        renderer()
    except Exception as exc:
        st.error(f"{title}: modulo isolato ({type(exc).__name__}). Le altre sezioni restano utilizzabili.")
        with st.expander("Dettaglio diagnostico"):
            st.code("".join(traceback.format_exception_only(type(exc), exc)).strip())


def render_unified_application() -> None:
    if "normalized_app_state" not in st.session_state:
        st.session_state.normalized_app_state = NormalizedAppState()
    state: NormalizedAppState = st.session_state.normalized_app_state

    with st.sidebar:
        st.header("Architect Advisor")
        view = st.selectbox("Applicazione", ["Vista completa", "Versione stabile", "Foundation multi-cloud", "Modalità diagnostica"], index=["Vista completa", "Versione stabile", "Foundation multi-cloud", "Modalità diagnostica"].index(state.active_view))
        mode = st.radio("Modalità", ["Demo", "Simulation", "Read-only"], index=["Demo", "Simulation", "Read-only"].index(state.operating_mode))
        forced_failure = None
        if view == "Modalità diagnostica":
            forced_failure = st.selectbox("Simula guasto modulo", [None, "multicloud", "stable_lab", "governance", "terraform", "finops"], format_func=lambda value: "Nessun guasto" if value is None else value)
        st.session_state.normalized_app_state = state.evolve(active_view=view, operating_mode=mode)
        st.markdown(f"**Versione attiva:** `{UNIFIED_VERSION}`")
        st.markdown(f"**Modalità attiva:** `{mode}`")
        st.markdown(f"**Ultimo commit stabile:** `{STABLE_COMMIT}`")
        if st.button("Torna al fallback", type="secondary", use_container_width=True):
            st.session_state.normalized_app_state = state.evolve(active_view="Versione stabile")
            st.rerun()

        st.divider(); st.caption("Stato moduli")
        for item in probe_modules(forced_failure):
            icon = "🟢" if item.status is HealthStatus.AVAILABLE else "🟠" if item.status is HealthStatus.DEGRADED else "🔴"
            st.write(f"{icon} **{item.label}** · {item.status.value}")
            st.caption(item.detail)

    st.caption(f"Stato condiviso normalizzato schema {state.schema_version} · nessuna connessione cloud · terraform apply disabilitato")
    if view == "Versione stabile":
        st.title("Versione stabile")
        _safe_section("Project Designer e laboratorio", render_platform_lab, "stable_lab", forced_failure)
        return
    if view == "Foundation multi-cloud":
        _safe_section("Foundation multi-cloud", render_multicloud_platform, "multicloud", forced_failure)
        return

    orchestrator, governance = foundation_runtime()
    st.title("Vista completa")
    sections = st.tabs(["Panoramica", "Progetto e simulazioni", "Storico e IaC", "Governance", "FinOps"])
    with sections[0]: _safe_section("Panoramica e dati multi-cloud", lambda: render_multicloud_overview(orchestrator), "multicloud", forced_failure)
    with sections[1]: _safe_section("Project Designer, controlli e simulazioni", render_platform_lab, "stable_lab", forced_failure)
    with sections[2]:
        _safe_section("Storico e confronto", lambda: render_scenario_history(orchestrator), "multicloud", forced_failure)
        st.info("Terraform, validazione e CI/CD restano nel laboratorio stabile della sezione precedente; condividono solo il contratto di stato versionato.")
    with sections[3]: _safe_section("Governance Control Plane e orchestratore", lambda: render_governance_plane(orchestrator, governance), "governance", forced_failure)
    with sections[4]:
        health = next(item for item in probe_modules(forced_failure) if item.module_id == "finops")
        if health.status is HealthStatus.AVAILABLE:
            from v2.modules.finops_dashboard import render_finops
            _safe_section("FinOps trasversale", render_finops, "finops", forced_failure)
        else:
            st.warning("FinOps è Degraded/Unavailable: il modulo è riservato ma non ancora implementato. Le altre sezioni restano operative.")
