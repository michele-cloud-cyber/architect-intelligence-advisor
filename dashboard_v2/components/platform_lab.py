"""Streamlit presentation for Platform Lab phase one and the secure S3 slice."""

from __future__ import annotations

import json

import streamlit as st

from v2.modules.platform_lab import (
    OperatingMode,
    ProjectDefinition,
    analyze_project,
    evaluate_controls,
    generate_s3_package,
    github_actions_example,
    simulate_s3_changes,
    validate_s3_package,
)
from v2.modules.platform_lab.scoring import overall_score


MODE_COLORS = {"Demo": "#2563eb", "Simulation": "#7c3aed", "AWS Read-only": "#64748b"}
SCORE_COLORS = ((80, "#22c55e"), (60, "#eab308"), (40, "#f97316"), (0, "#ef4444"))


def render_platform_lab() -> None:
    st.title("AWS Interactive Architecture, Security & Terraform Lab")
    st.caption("Design → analyze → simulate → generate → validate. No AWS mutation or Terraform apply.")

    mode_label = st.radio("Operating mode", ["Demo", "Simulation"], horizontal=True, key="lab_mode")
    mode = OperatingMode(mode_label)
    color = MODE_COLORS[mode_label]
    st.markdown(
        f'<span style="background:{color};color:white;padding:.35rem .75rem;border-radius:999px;font-weight:700">MODE · {mode_label.upper()}</span>',
        unsafe_allow_html=True,
    )
    st.caption("AWS Read-only is architecture-only in Phase 1 and is not connected.")

    project = _project_designer(mode)
    analysis = analyze_project(project)
    results, scores = evaluate_controls(project.configuration)

    st.divider()
    st.header("Analysis and scores")
    _render_analysis(analysis)
    _render_scores(scores)
    selected_changes = _render_controls(results)

    st.divider()
    st.header("Before / after simulation")
    st.caption("SIMULATION · deterministic local rules; not an AWS check and not an estimate produced by AI.")
    if st.button("Simulate selected changes", type="primary", disabled=not selected_changes):
        st.session_state["lab_simulation"] = simulate_s3_changes(project.configuration, tuple(selected_changes))
        st.session_state.pop("lab_package", None)

    simulation = st.session_state.get("lab_simulation")
    if simulation is None:
        st.info("Select controls in the table and run the simulation to unlock the decision and Terraform stages.")
        return
    _render_simulation(simulation)

    st.divider()
    st.header("Approved decision → Terraform")
    _render_decision(simulation, project)
    if st.button("Generate Terraform", type="primary"):
        st.session_state["lab_package"] = generate_s3_package(project, simulation)
    package = st.session_state.get("lab_package")
    if package is None:
        return
    _render_package(package)


def _project_designer(mode: OperatingMode) -> ProjectDefinition:
    st.header("Project Designer")
    with st.form("project_designer"):
        left, right = st.columns(2)
        with left:
            name = st.text_input("Project name", "Secure S3 Landing Zone Lab")
            objective = st.text_input("Objective", "Protect business artifacts in Amazon S3")
            description = st.text_area("Free project description", "A private S3 workload bucket containing confidential architecture artifacts.")
            services = st.multiselect("AWS services", ["S3", "IAM", "CloudTrail", "KMS", "CloudWatch", "AWS Config"], ["S3", "IAM", "CloudTrail"])
            accounts = st.text_input("Accounts", "sandbox-account")
            environments = st.multiselect("Environments", ["development", "staging", "production"], ["development"])
            regions = st.multiselect("Regions", ["eu-west-1", "eu-central-1", "eu-south-1", "us-east-1"], ["eu-west-1"])
            identities = st.text_area("Users, groups and roles", "Application role and read-only audit role")
        with right:
            classification = st.selectbox("Data sensitivity", ["Public", "Internal", "Confidential", "Restricted"], index=2)
            network = st.text_input("Network requirements", "TLS-only access; no public endpoint use")
            security = st.text_input("Security requirements", "Private, encrypted, versioned, logged and least privilege")
            compliance = st.text_input("Compliance and audit", "Access evidence retained for audit")
            availability = st.text_input("Availability", "Regional S3 durability; recovery from accidental overwrite")
            backup = st.text_input("Backup and disaster recovery", "Versioning with 90-day noncurrent retention")
            budget = st.text_input("Monthly budget", "EUR 50")
            recovery_left, recovery_right = st.columns(2)
            rto = recovery_left.number_input("RTO hours", min_value=0, value=4)
            rpo = recovery_right.number_input("RPO hours", min_value=0, value=1)
            constraints = st.text_input("Business constraints", "No credentials in code; manual approval before apply")
        st.form_submit_button("Analyze project")

    demo = mode == OperatingMode.DEMO
    defaults = {
        "block_public_access": False, "encryption": False, "versioning": False,
        "logging": False, "enforce_tls": False, "least_privilege": True,
        "monitoring": False, "lifecycle": False,
    }
    if mode == OperatingMode.SIMULATION:
        st.subheader("Current simulated configuration")
        columns = st.columns(4)
        labels = {
            "block_public_access": "Block public access", "encryption": "Encryption",
            "versioning": "Versioning", "logging": "Access logging", "enforce_tls": "TLS policy",
            "least_privilege": "Least privilege", "monitoring": "Monitoring", "lifecycle": "Lifecycle",
        }
        for index, (key, label) in enumerate(labels.items()):
            defaults[key] = columns[index % 4].checkbox(label, value=defaults[key], key=f"current_{key}")
    else:
        st.info("Demo provenance: fictional configuration with only least privilege enabled.")
    return ProjectDefinition(
        name, objective, description, tuple(services), tuple(item.strip() for item in accounts.split(",") if item.strip()),
        tuple(environments), tuple(regions), identities, classification, network, security, compliance,
        availability, backup, budget, int(rto), int(rpo), constraints, mode, defaults,
    )


def _render_analysis(analysis) -> None:
    columns = st.columns(4)
    for column, title, values in zip(columns, ("Missing", "Contradictions", "Risks", "Dependencies"), (analysis.missing_information, analysis.contradictions, analysis.risks, analysis.dependencies)):
        with column.container(border=True):
            st.metric(title, len(values))
            for value in values[:3]:
                st.caption(f"• {value}")


def _render_scores(scores: dict[str, int | None]) -> None:
    columns = st.columns(4)
    for index, (category, score) in enumerate(scores.items()):
        color = "#64748b" if score is None else next(color for threshold, color in SCORE_COLORS if score >= threshold)
        value = "N/A" if score is None else f"{score}/100"
        columns[index % 4].markdown(
            f'<div style="border:1px solid #334155;border-left:6px solid {color};padding:1rem;border-radius:.6rem;margin-bottom:1rem"><small>{category}</small><h3>{value}</h3></div>',
            unsafe_allow_html=True,
        )


def _render_controls(results) -> list[str]:
    st.subheader("Granular controls")
    rows = [{
        "Simulate change": item.score == 0,
        "Control": item.definition.control_id,
        "Category": item.definition.category,
        "Current configuration": item.current_value,
        "Status": item.status.value,
        "Risk": item.definition.description,
        "Severity": item.severity,
        "Reason": item.rationale,
        "Remediation": item.definition.remediation,
        "Indicative cost": item.definition.estimated_monthly_cost,
        "Confidence": f"{item.confidence}%",
        "Input key": item.definition.input_key,
    } for item in results]
    edited = st.data_editor(
        rows, hide_index=True, width="stretch", disabled=[key for key in rows[0] if key != "Simulate change"],
        column_config={"Simulate change": st.column_config.CheckboxColumn("Simulate change")},
        key="lab_controls",
    )
    return [row["Input key"] for row in edited if row["Simulate change"]]


def _render_simulation(simulation) -> None:
    before, after, delta, percent = st.columns(4)
    before.metric("Before", f"{simulation.before_overall}/100")
    after.metric("After", f"{simulation.after_overall}/100")
    delta.metric("Absolute change", f"+{simulation.absolute_delta}")
    percent.metric("Relative change", f"+{simulation.percentage_delta}%")
    st.caption("Relative change = absolute delta ÷ initial score. Category and control weights are declared in scoring.py.")
    st.dataframe(list(simulation.contributions), hide_index=True, width="stretch")
    columns = st.columns(3)
    columns[0].success("Eliminated risks\n\n" + ("\n\n".join(f"• {item}" for item in simulation.eliminated_risks) or "• None"))
    columns[1].warning("Residual risks\n\n" + ("\n\n".join(f"• {item}" for item in simulation.residual_risks) or "• None"))
    columns[2].info("New risks\n\n" + ("\n\n".join(f"• {item}" for item in simulation.new_risks) or "• None"))
    st.write(f"**Operational impact:** {simulation.operational_impact}")
    st.write(f"**Estimated cost:** {simulation.estimated_cost} · **Confidence:** {simulation.confidence}%")


def _render_decision(simulation, project) -> None:
    summary = {
        "Decision": "Private, encrypted, versioned S3 bucket with logging and total public access block",
        "Target account": project.accounts[0] if project.accounts else "Not supplied",
        "Region": project.regions[0] if project.regions else "Not supplied",
        "Environment": project.environments[0] if project.environments else "Not supplied",
        "Before / after": f"{simulation.before_overall} → {simulation.after_overall}",
        "Confidence": f"{simulation.confidence}% deterministic simulation",
    }
    st.table([summary])
    st.warning("Generation is local only. No plan, apply, AWS mutation, repository publication, or backend creation is performed.")


def _render_package(package) -> None:
    summary_tab, code_tab, validation_tab, pipeline_tab = st.tabs(["Decision", "Terraform files", "Validation & security", "CI/CD example"])
    with summary_tab:
        st.json(package.decision_summary)
    with code_tab:
        selected = st.selectbox("Generated file", list(package.files))
        language = "hcl" if selected.endswith((".tf", ".hcl", ".tfvars")) else "markdown"
        st.code(package.files[selected], language=language)
        st.caption("Package export will be added in Phase 2. Files are generated in memory in Phase 1.")
    with validation_tab:
        checks = validate_s3_package(package)
        st.dataframe([item.__dict__ for item in checks], hide_index=True, width="stretch")
        passed = sum(item.status == "Passed" for item in checks)
        st.success(f"{passed} deterministic Policy as Code checks passed.")
        st.info("Terraform CLI, TFLint, Checkov and real plan remain Not executed unless explicitly run in a reviewed local workflow.")
    with pipeline_tab:
        st.code(github_actions_example(), language="yaml")
        st.caption("Example only · not published · pull requests never apply infrastructure.")
