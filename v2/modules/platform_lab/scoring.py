"""Transparent deterministic scoring rules for the phase-one S3 slice."""

from __future__ import annotations

from collections import defaultdict

from v2.modules.platform_lab.models import (
    ControlDefinition,
    ControlResult,
    ProjectAnalysis,
    ProjectDefinition,
    ResultStatus,
)


CATEGORIES = (
    "Security",
    "IAM & Access Control",
    "Network",
    "Audit & Compliance",
    "Data Protection",
    "Reliability",
    "Operational Excellence",
    "Cost Optimization",
)

S3_CONTROLS = (
    ControlDefinition("S3-PUB-001", "Security", "Block all public S3 access", "block_public_access", 25, "Enable all S3 public access block flags.", "aws_s3_bucket_public_access_block", "test_public_access_block"),
    ControlDefinition("S3-TLS-001", "Network", "Require TLS for every S3 request", "enforce_tls", 15, "Add an explicit deny for insecure transport.", "aws_s3_bucket_policy.aws:SecureTransport", "test_tls_policy"),
    ControlDefinition("S3-IAM-001", "IAM & Access Control", "Use scoped bucket permissions", "least_privilege", 20, "Grant only required S3 actions and resources.", "aws_iam_policy / aws_s3_bucket_policy", "test_no_unjustified_wildcard"),
    ControlDefinition("S3-ENC-001", "Data Protection", "Encrypt objects at rest", "encryption", 25, "Configure default S3 server-side encryption.", "aws_s3_bucket_server_side_encryption_configuration", "test_default_encryption"),
    ControlDefinition("S3-VER-001", "Reliability", "Enable bucket versioning", "versioning", 20, "Enable S3 versioning for recovery.", "aws_s3_bucket_versioning", "test_versioning_enabled"),
    ControlDefinition("S3-LOG-001", "Audit & Compliance", "Enable server access logging", "logging", 20, "Send access logs to a dedicated protected bucket.", "aws_s3_bucket_logging", "test_access_logging", "$1–5 depending on traffic"),
    ControlDefinition("S3-MON-001", "Operational Excellence", "Enable observable access events", "monitoring", 10, "Monitor access and configuration changes.", "aws_cloudwatch_metric_alarm / CloudTrail data events", "test_monitoring_declared", "$1–10 depending on events"),
    ControlDefinition("S3-LCY-001", "Cost Optimization", "Define lifecycle management", "lifecycle", 10, "Expire or transition old versions and logs.", "aws_s3_bucket_lifecycle_configuration", "test_lifecycle_rule"),
)


def evaluate_controls(configuration: dict[str, bool | str]) -> tuple[list[ControlResult], dict[str, int | None]]:
    results: list[ControlResult] = []
    grouped: dict[str, list[tuple[int, int]]] = defaultdict(list)
    for control in S3_CONTROLS:
        raw = configuration.get(control.input_key)
        if raw is None or raw == "unknown":
            result = ControlResult(control, "Unknown", 0, ResultStatus.INSUFFICIENT, "Unknown", "No evidence was provided; this control is excluded from the score.", 0)
        elif bool(raw):
            result = ControlResult(control, "Enabled", 100, ResultStatus.CORRECT, "Low", f"{control.control_id} is satisfied by the supplied configuration.", 100)
            grouped[control.category].append((100, control.weight))
        else:
            severity = "Critical" if control.weight >= 25 else "High" if control.weight >= 20 else "Medium"
            status = ResultStatus.HIGH_RISK if severity in {"Critical", "High"} else ResultStatus.MEDIUM_RISK
            result = ControlResult(control, "Disabled", 0, status, severity, f"{control.control_id} is not satisfied; its declared weight is {control.weight}.", 100)
            grouped[control.category].append((0, control.weight))
        results.append(result)

    scores: dict[str, int | None] = {}
    for category in CATEGORIES:
        values = grouped.get(category, [])
        scores[category] = round(sum(score * weight for score, weight in values) / sum(weight for _, weight in values)) if values else None
    return results, scores


def overall_score(scores: dict[str, int | None]) -> int:
    evaluated = [value for value in scores.values() if value is not None]
    return round(sum(evaluated) / len(evaluated)) if evaluated else 0


def analyze_project(project: ProjectDefinition) -> ProjectAnalysis:
    missing = []
    for label, value in (
        ("objective", project.objective), ("security requirements", project.security_requirements),
        ("backup and disaster recovery", project.backup_dr), ("budget", project.budget),
    ):
        if not value.strip():
            missing.append(label)
    contradictions = []
    if project.data_classification.lower() in {"confidential", "restricted"} and not project.configuration.get("encryption"):
        contradictions.append("Sensitive data is declared while default encryption is disabled.")
    risks = tuple(result.definition.description for result in evaluate_controls(project.configuration)[0] if result.score == 0 and result.status != ResultStatus.INSUFFICIENT)
    dependencies = (
        "Access logging requires a separate protected log destination.",
        "Versioning should be paired with lifecycle rules to control retained-object cost.",
    )
    improvements = tuple(result.definition.remediation for result in evaluate_controls(project.configuration)[0] if result.score == 0)
    return ProjectAnalysis(tuple(missing), tuple(contradictions), risks, dependencies, improvements)
