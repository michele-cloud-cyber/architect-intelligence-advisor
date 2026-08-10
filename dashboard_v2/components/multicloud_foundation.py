"""Four-part UI for the provider-neutral multi-cloud foundation."""

from __future__ import annotations

from datetime import datetime, timezone
import uuid

import streamlit as st

from v2.modules.multicloud_foundation import (
    GovernanceControlPlane, LocalScenarioHistory, MultiCloudOrchestrator,
    OperationalLevel, PluginManifest, PluginRegistry, Provider, ScenarioSnapshot,
    adapter_registry,
)
from dashboard_v2.components.platform_lab import render_platform_lab


def _runtime():
    if "mc_history" not in st.session_state:
        st.session_state.mc_history = LocalScenarioHistory()
    if "mc_plugins" not in st.session_state:
        registry = PluginRegistry(("demo-cmdb",))
        registry.register(PluginManifest(
            "demo-cmdb", "1.0.0", ("inventory-read",), ("resource-metadata",), (),
            ("inventory:read",), (Provider.AWS, Provider.AZURE, Provider.GCP),
            {"scope": "string"}, {"resources": "array"}, 10,
            "fail-closed", True, "demo-only",
        ))
        st.session_state.mc_plugins = registry
    governance = GovernanceControlPlane()
    return MultiCloudOrchestrator(adapter_registry(), governance, st.session_state.mc_history, st.session_state.mc_plugins), governance


def render_multicloud_platform() -> None:
    orchestrator, governance = _runtime()
    st.title("Adaptive Multi-Cloud Landing Zone Orchestrator")
    st.caption("Foundation demo · AWS, Azure and GCP synthetic data · no credentials, SDKs, network calls or apply")
    parts = st.tabs([
        "Parte 1 · Panoramica", "Parte 2 · Interazione e simulazione",
        "Parte 3 · Storico e IaC", "Parte 4 · Governance",
    ])
    with parts[0]:
        _overview(orchestrator)
    with parts[1]:
        st.info("Il laboratorio esistente resta operativo e usa solo configurazioni locali simulate.")
        render_platform_lab()
    with parts[2]:
        _history(orchestrator)
    with parts[3]:
        _governance(orchestrator, governance)


def _overview(orchestrator: MultiCloudOrchestrator) -> None:
    st.header("Stato complessivo della landing zone")
    selected = st.multiselect("Provider", [p.value for p in (Provider.AWS, Provider.AZURE, Provider.GCP)], [p.value for p in (Provider.AWS, Provider.AZURE, Provider.GCP)])
    query = st.text_input("Ricerca risorse, account/subscription/project o regione")
    providers = tuple(Provider(value) for value in selected)
    models = orchestrator.overview(providers)
    rows = []
    for model in models:
        for resource in model.resources:
            row = {"Provider": resource.provider.value, "Organizzazione": resource.organization, "Scope": resource.scope, "Ambiente": resource.environment, "Regione": resource.region, "Dominio": resource.domain, "Risorsa": resource.resource_type, "Nome": resource.name, "Costo demo/mese": resource.monthly_cost, "Badge": model.evidence_mode.value, "Attuale": str(resource.current), "Desiderato": str(resource.desired)}
            if not query or query.lower() in " ".join(str(v).lower() for v in row.values()): rows.append(row)
    a,b,c,d=st.columns(4); a.metric("Provider",len(models)); b.metric("Scope",len({r["Scope"] for r in rows})); c.metric("Risorse",len(rows)); d.metric("Maturità demo","42/100")
    st.dataframe(rows,hide_index=True,width="stretch")
    chart=[{"provider":r["Provider"],"current":35,"desired":78,"category":"Security"} for r in rows]
    if chart:
        st.vega_lite_chart({"values":chart},{"mark":"bar","encoding":{"x":{"field":"provider","type":"nominal"},"y":{"field":"desired","type":"quantitative","scale":{"domain":[0,100]}},"color":{"field":"provider","type":"nominal"},"tooltip":[{"field":"provider"},{"field":"current"},{"field":"desired"}]}},width="stretch")
    st.caption("Tutti i valori sono sintetici. Le fonti JSON/YAML, Terraform, API read-only, CMDB, Security e FinOps sono contratti futuri, non connessioni attive.")


def _history(orchestrator: MultiCloudOrchestrator) -> None:
    st.header("Scenari locali e confronto attuale/desiderato")
    provider = Provider(st.selectbox("Provider scenario", [p.value for p in (Provider.AWS, Provider.AZURE, Provider.GCP)]))
    name = st.text_input("Nome scenario", "Scenario consigliato")
    rationale = st.text_input("Motivazione", "Ridurre esposizione e aumentare cifratura")
    if st.button("Salva snapshot locale", type="primary"):
        current = orchestrator.adapters[provider].load_demo()
        desired = current
        snapshot = ScenarioSnapshot(str(uuid.uuid4()), name, datetime.now(timezone.utc).isoformat(), "local-demo-user", rationale, current, desired, {"technical": 42, "maturity": 38, "desired": 78}, ("Synthetic encryption finding",))
        orchestrator.history.append(snapshot)
        st.success("Snapshot immutabile salvato solo nella sessione locale.")
    snapshots = orchestrator.history.list()
    st.dataframe([{"ID":s.scenario_id,"Nome":s.name,"Data":s.created_at,"Autore":s.author,"Motivazione":s.rationale,"Approvazione":s.approval_status} for s in snapshots],hide_index=True,width="stretch")
    st.subheader("Flusso controllato")
    st.code("attuale → desiderato → simulazione → storico → decisione → codice → test → plan → approvazione",language=None)
    st.caption("Gli snapshot non vengono modificati retroattivamente. Export cloud, plan e apply non sono eseguiti.")


def _governance(orchestrator: MultiCloudOrchestrator, governance: GovernanceControlPlane) -> None:
    st.header("Governance Control Plane e orchestratore")
    st.warning("Fail-closed: plan, approvazione e apply controllato sono bloccati in questa foundation locale.")
    st.dataframe(orchestrator.execution_plan((Provider.AWS,Provider.AZURE,Provider.GCP)),hide_index=True,width="stretch")
    st.subheader("Plugin registrati")
    st.dataframe([{"Nome":p.name,"Versione":p.version,"Capability":", ".join(p.capabilities),"Permessi":", ".join(p.permissions),"Timeout":p.timeout_seconds,"Audit":p.audit_enabled,"Affidabilità":p.trust_status} for p in orchestrator.plugins.manifests()],hide_index=True,width="stretch")
    sample=st.text_input("Prova redazione", "password=demo-value")
    st.code(governance.redact(sample))
    decision=governance.authorize(OperationalLevel.CONTROLLED_APPLY)
    st.error("Apply controllato: BLOCCATO · "+"; ".join(decision.reasons))
