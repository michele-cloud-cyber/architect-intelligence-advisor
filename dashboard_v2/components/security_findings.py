"""Streamlit presentation for the isolated Security Findings dossier."""

from __future__ import annotations

import streamlit as st

from v2.modules.security_findings.models import SecurityCase


def render_security_findings(dossier: SecurityCase) -> None:
    """Render an existing dossier without adding security-analysis logic to the UI."""

    st.subheader("Security Findings")
    st.caption("Demo-only investigative dossier. No AWS, Bedrock, network, or scanner calls are made.")

    overview, findings, evidence, risk, attack_path, timeline, reports = st.tabs(
        [
            "Overview",
            "Findings",
            "Evidence Locker",
            "Risk Score",
            "Possible Attack Path",
            "Timeline",
            "Reports",
        ]
    )

    with overview:
        _render_overview(dossier)
    with findings:
        _render_findings(dossier)
    with evidence:
        _render_evidence(dossier)
    with risk:
        _render_risk(dossier)
    with attack_path:
        _render_attack_path(dossier)
    with timeline:
        _render_timeline(dossier)
    with reports:
        _render_reports(dossier)


def _render_overview(dossier: SecurityCase) -> None:
    st.markdown(f"#### {dossier.title}")
    st.write(dossier.description)
    columns = st.columns(4)
    columns[0].metric("Case ID", dossier.case_id)
    columns[1].metric("Status", dossier.status.value.replace("_", " ").title())
    columns[2].metric("Severity", dossier.severity.value.title())
    columns[3].metric("Confidence", f"{dossier.confidence_score}%")
    st.caption(f"Internal UUID: `{dossier.case_uuid}`")
    st.caption(
        f"First detected: {_date_label(dossier.first_detected)} · "
        f"Last observed: {_date_label(dossier.last_observed)}"
    )
    st.write(f"**Landing Zone:** {dossier.landing_zone or 'Not available'}")
    st.write(f"**Scope:** account `{dossier.cloud_account_id or 'N/A'}` · region `{dossier.cloud_region or 'N/A'}`")
    st.write(f"**Technical impact:** {dossier.technical_impact}")
    st.write(f"**Possible business impact:** {dossier.business_impact}")


def _render_findings(dossier: SecurityCase) -> None:
    st.caption(f"{len(dossier.findings)} normalized findings correlated into this Security Case.")
    st.dataframe(
        [
            {
                "Finding ID": finding.finding_id,
                "Source": finding.source.value,
                "Severity": finding.severity.value.title(),
                "CVSS": finding.cvss,
                "CVE": ", ".join(finding.cves) or "—",
                "CWE": ", ".join(finding.cwes) or "—",
                "MITRE ATT&CK": ", ".join(finding.mitre_attack) or "—",
                "Asset": finding.asset_id,
                "Endpoint": _endpoint_label(finding.ip_address, finding.port, finding.protocol),
                "Service": finding.service or "—",
            }
            for finding in dossier.findings
        ],
        hide_index=True,
        use_container_width=True,
    )
    st.markdown("**Correlation evidence**")
    for correlation in dossier.correlations:
        st.info(
            f"{correlation.level.value.title()} confidence ({correlation.confidence_score}%): "
            f"{correlation.explanation}"
        )


def _render_evidence(dossier: SecurityCase) -> None:
    st.caption("Evidence is fingerprinted deterministically and bound to this dossier.")
    st.dataframe(
        [
            {
                "Evidence ID": item.evidence_id,
                "Finding": item.finding_id,
                "Source": item.source.value,
                "Resource": item.resource_id,
                "Reliability": f"{item.reliability:.0%}",
                "Fingerprint": item.fingerprint,
            }
            for item in dossier.evidence
        ],
        hide_index=True,
        use_container_width=True,
    )
    for item in dossier.evidence:
        with st.expander(item.evidence_id):
            st.write(item.description)
            st.caption(f"Observed value: {item.observed_value}")
            st.caption(f"Source reference: {item.source_reference}")


def _render_risk(dossier: SecurityCase) -> None:
    if dossier.risk is None:
        st.info("No explainable risk score is available.")
        return
    st.metric("Contextual Risk Score", f"{dossier.risk.score}/100", dossier.risk.level.value.title())
    st.write(dossier.risk.explanation)
    st.caption(dossier.risk.formula)
    st.dataframe(
        [
            {
                "Component": item.name,
                "Score": item.score,
                "Maximum": item.maximum,
                "Type": "Reduction" if item.reduction else "Contribution",
                "Rationale": item.rationale,
            }
            for item in dossier.risk.components
        ],
        hide_index=True,
        use_container_width=True,
    )


def _render_attack_path(dossier: SecurityCase) -> None:
    if dossier.attack_path is None:
        st.info("No possible attack path is available.")
        return
    st.warning(dossier.attack_path.disclaimer)
    st.caption(f"Correlation confidence: {dossier.attack_path.confidence_score}%")
    st.graphviz_chart(_attack_path_dot(dossier.attack_path.steps), use_container_width=True)
    for index, step in enumerate(dossier.attack_path.steps, start=1):
        st.write(f"{index}. {step}")


def _render_timeline(dossier: SecurityCase) -> None:
    st.dataframe(
        [
            {
                "Timestamp": event.timestamp.isoformat(),
                "Event": event.event_type.replace("_", " ").title(),
                "Description": event.description,
                "Source": event.source.value,
                "Status": event.status_change or "—",
                "Risk change": _risk_change(event.previous_risk_score, event.new_risk_score),
            }
            for event in dossier.timeline
        ],
        hide_index=True,
        use_container_width=True,
    )


def _render_reports(dossier: SecurityCase) -> None:
    st.markdown("#### Attack Story")
    st.markdown(dossier.attack_story, unsafe_allow_html=False)
    st.markdown("#### Priority Remediation")
    for index, action in enumerate(dossier.remediation, start=1):
        st.write(f"{index}. {action}")


def _attack_path_dot(steps: tuple[str, ...]) -> str:
    nodes = [f'node{index} [label="{_dot_escape(step)}"];' for index, step in enumerate(steps)]
    edges = [f"node{index} -> node{index + 1};" for index in range(len(steps) - 1)]
    return "digraph attack_path { rankdir=LR; node [shape=box, style=rounded]; " + " ".join(nodes + edges) + " }"


def _dot_escape(value: str) -> str:
    return value.replace("\\", "\\\\").replace('"', '\\"')


def _date_label(value) -> str:
    return value.isoformat() if value is not None else "Not available"


def _endpoint_label(ip_address: str | None, port: int | None, protocol: str | None) -> str:
    if ip_address is None:
        return "—"
    return f"{ip_address}:{port or '—'} {protocol or ''}".strip()


def _risk_change(previous: int | None, current: int | None) -> str:
    if previous is None and current is None:
        return "—"
    return f"{previous if previous is not None else '—'} → {current if current is not None else '—'}"
