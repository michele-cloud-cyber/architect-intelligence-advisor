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
from dashboard_v2.components.code_architecture import render_code_architecture
from dashboard_v2.components.security_findings import render_vulnerability_intelligence
from dashboard_v2.components.ai_bedrock_advisory import render_ai_bedrock_advisory
from dashboard_v2.components.command_palette import render_command_palette
from v2.modules.security_findings.service import build_demo_security_case
from v2.modules.unified_shell import HealthStatus, MODULE_REGISTRY, NormalizedAppState, get_module, probe_modules, search_modules


STABLE_COMMIT = "7e1db43"
FOUNDATION_COMMIT = "45722f1"
UNIFIED_VERSION = "3.0.0"

SHELL_TEXT={
"it":{"app":"Applicazione","mode":"Modalità","complete":"Vista completa","stable":"Versione stabile","foundation":"Foundation multi-cloud","diagnostic":"Modalità diagnostica","failure":"Simula guasto modulo","none":"Nessun guasto","version":"Versione attiva","active":"Modalità attiva","commit":"Ultimo commit stabile","fallback":"Torna al fallback","health":"Stato moduli","overview":"Panoramica","design":"Design e simulazione","code":"Code & Test Lab","governance":"Governance","onboarding":"Benvenuto nella V3.0: parti dai requisiti nel Design oppure importa Terraform nel Code & Test Lab. Tutte le analisi sono locali, statiche o simulate.","reset":"Reset dati demo"},
"en":{"app":"Application","mode":"Mode","complete":"Complete view","stable":"Stable version","foundation":"Multi-cloud foundation","diagnostic":"Diagnostic mode","failure":"Simulate module failure","none":"No failure","version":"Active version","active":"Active mode","commit":"Last stable commit","fallback":"Return to fallback","health":"Module status","overview":"Overview","design":"Design & simulation","code":"Code & Test Lab","governance":"Governance","onboarding":"Welcome to V3.0: start from requirements in Design or import Terraform in Code & Test Lab. Every analysis is local, static or simulated.","reset":"Reset demo data"}}


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
        language=st.radio("Lingua / Language",["Italiano","English"],horizontal=True); lang="it" if language=="Italiano" else "en"; tx=SHELL_TEXT[lang]
        canonical=["Vista completa","Versione stabile","Foundation multi-cloud","Modalità diagnostica"]
        labels=[tx["complete"],tx["stable"],tx["foundation"],tx["diagnostic"]]
        chosen = st.selectbox(tx["app"], labels, index=canonical.index(state.active_view)); view=canonical[labels.index(chosen)]
        mode = st.radio(tx["mode"], ["Demo", "Simulation", "Read-only"], index=["Demo", "Simulation", "Read-only"].index(state.operating_mode))
        forced_failure = None
        if view == "Modalità diagnostica":
            forced_failure = st.selectbox(tx["failure"], [None,*[item.module_id for item in MODULE_REGISTRY]], format_func=lambda value: tx["none"] if value is None else value)
        st.session_state.normalized_app_state = state.evolve(active_view=view, operating_mode=mode)
        st.markdown(f"**{tx['version']}:** `{UNIFIED_VERSION}`")
        st.markdown(f"**{tx['active']}:** `{mode}`")
        st.markdown(f"**{tx['commit']}:** `{STABLE_COMMIT}`")
        if st.button(tx["fallback"], type="secondary", use_container_width=True):
            st.session_state.normalized_app_state = state.evolve(active_view="Versione stabile")
            st.rerun()

        if st.button(tx["reset"],use_container_width=True):
            for key in ("v3_bundle","v3_original","v3_sim","lab_simulation","lab_package","mc_history"):
                st.session_state.pop(key,None)
            st.rerun()
        st.divider()
        query=st.text_input("Cerca funzione…" if lang=="it" else "Search function…",key="global_function_search",placeholder="CVE, costi, Bedrock, Terraform, IMDS…")
        for result in search_modules(query,lang)[:6]:
            health=next((item for item in probe_modules(forced_failure) if item.module_id==result.module_id),None)
            status=health.status.value if health else "Disabled"
            if st.button(f"{result.name(lang)} · {status} · {result.badge}",key=f"search_{result.module_id}",use_container_width=True,help=result.description(lang)):
                st.query_params["module"]=result.module_id; st.rerun()
        st.markdown("<style>.st-key-global_nav_targets{display:none!important}</style>",unsafe_allow_html=True)
        with st.container(key="global_nav_targets"):
            for module in MODULE_REGISTRY:
                if st.button(f"navigate::{module.module_id}",key=f"nav_target_{module.module_id}"):
                    st.query_params["module"]=module.module_id; st.rerun()
        st.divider(); st.caption(tx["health"])
        for item in probe_modules(forced_failure):
            icon = "🟢" if item.status is HealthStatus.AVAILABLE else "🟠" if item.status is HealthStatus.DEGRADED else "🔴"
            st.write(f"{icon} **{item.label}** · {item.status.value}")
            st.caption(item.detail)

    render_command_palette(lang)
    st.info(tx["onboarding"])
    st.caption(f"Normalized shared state schema {state.schema_version} · Demo / Simulation-only · synthetic data · no credentials · no cloud mutations · no automatic apply")
    if view == "Versione stabile":
        st.title("Versione stabile")
        _safe_section("Project Designer e laboratorio", render_platform_lab, "stable_lab", forced_failure)
        return
    if view == "Foundation multi-cloud":
        _safe_section("Foundation multi-cloud", render_multicloud_platform, "multicloud", forced_failure)
        return

    orchestrator, governance = foundation_runtime()
    routed_id=st.query_params.get("module")
    routed=get_module(routed_id) if routed_id else None
    if routed:
        if st.button("← Vista completa" if lang=="it" else "← Complete view"):
            st.query_params.pop("module",None); st.rerun()
        st.title(routed.name(lang)); st.caption(f"{routed.destination} · {routed.badge} · {routed.description(lang)}")
        _render_registered_module(routed.module_id,lang,orchestrator,governance,forced_failure)
        return
    st.title(tx["complete"])
    area_ids=("overview","stable_lab","code_architecture","governance")
    area_names=[get_module(item).name(lang) if item!="code_architecture" else tx["code"] for item in area_ids]
    sections = st.tabs(area_names)
    with sections[0]: _safe_section("Panoramica e dati multi-cloud", lambda: render_multicloud_overview(orchestrator), "overview", forced_failure)
    with sections[1]: _safe_section("Project Designer, controls & simulations", render_platform_lab, "stable_lab", forced_failure)
    with sections[2]:
        architecture_tab,vulnerability_tab,ai_tab,history_tab=st.tabs(["Code → Architecture & Risk","Vulnerability Intelligence","AI & Bedrock Advisory","History / Storico"])
        with architecture_tab:_safe_section("Code → Architecture & Risk",lambda:render_code_architecture(lang),"code_architecture",forced_failure)
        with vulnerability_tab:_safe_section("Vulnerability Intelligence",lambda:render_vulnerability_intelligence(build_demo_security_case()),"vulnerability",forced_failure)
        with ai_tab:_safe_section("AI & Bedrock Advisory",lambda:render_ai_bedrock_advisory(lang),"ai_bedrock",forced_failure)
        with history_tab:_safe_section("Scenario history",lambda:render_scenario_history(orchestrator),"history",forced_failure)
    with sections[3]:
        _safe_section("Governance Control Plane & Orchestrator",lambda:render_governance_plane(orchestrator,governance),"governance",forced_failure)
        from v2.modules.finops_dashboard import render_finops
        _safe_section("Cross-cutting FinOps",render_finops,"finops",forced_failure)


def _render_registered_module(module_id,lang,orchestrator,governance,forced_failure):
    renderers={
        "overview":lambda:render_multicloud_overview(orchestrator),
        "stable_lab":render_platform_lab,
        "code_architecture":lambda:render_code_architecture(lang),
        "vulnerability":lambda:render_vulnerability_intelligence(build_demo_security_case()),
        "ai_bedrock":lambda:render_ai_bedrock_advisory(lang),
        "history":lambda:render_scenario_history(orchestrator),
        "governance":lambda:render_governance_plane(orchestrator,governance),
    }
    if module_id=="finops":
        from v2.modules.finops_dashboard import render_finops
        renderer=render_finops
    else: renderer=renderers[module_id]
    _safe_section(get_module(module_id).name(lang),renderer,module_id,forced_failure)
