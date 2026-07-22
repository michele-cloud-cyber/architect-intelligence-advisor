"""Transparent contextual risk calculation for an investigative Security Case."""

from __future__ import annotations

from statistics import mean
from typing import Iterable

from v2.modules.security_findings.models import ExplainableRiskScore, RiskComponent, RiskLevel, SecurityFinding


def calculate_risk(findings: Iterable[SecurityFinding]) -> ExplainableRiskScore:
    """Calculate a bounded score using documented, deterministic rules."""

    items = tuple(findings)
    if not items:
        return ExplainableRiskScore(0, RiskLevel.LOW, (), "score = 0", "No findings are present.")

    highest_cvss = max((item.cvss or 0 for item in items), default=0)
    average_confidence = mean(item.confidence for item in items)
    components = (
        RiskComponent("CVSS severity", round(highest_cvss / 10 * 30, 1), 30, f"Highest observed CVSS is {highest_cvss:.1f}."),
        RiskComponent("Internet reachability", 15 if any(item.internet_exposed for item in items) else 0, 15, "At least one affected asset is Internet-exposed." if any(item.internet_exposed for item in items) else "No Internet exposure was observed."),
        RiskComponent("Public exploit availability", 10 if any(item.exploit_available for item in items) else 0, 10, "A demo finding indicates public exploit availability." if any(item.exploit_available for item in items) else "No public exploit was observed."),
        RiskComponent("Active threat observed", 0, 10, "No active threat telemetry is included in the demo dataset."),
        RiskComponent("IAM privileges", 15 if any(item.identity_reference for item in items) else 0, 15, "Affected asset is associated with an IAM identity or role." if any(item.identity_reference for item in items) else "No IAM identity linkage was observed."),
        RiskComponent("Asset criticality", round(max(item.asset_criticality for item in items) * 10, 1), 10, "Derived from the demo asset criticality classification."),
        RiskComponent("Downstream access", 10 if any(item.downstream_resources for item in items) else 0, 10, "Affected asset can reach downstream demo resources." if any(item.downstream_resources for item in items) else "No downstream resources were observed."),
        RiskComponent("Evidence quality", round(average_confidence * 5, 1), 5, f"Average source confidence is {average_confidence:.0%}."),
        RiskComponent("Compensating controls", 0, 5, "No compensating controls are asserted by the demo evidence.", reduction=True),
    )
    additive = sum(component.score for component in components if not component.reduction)
    reductions = sum(component.score for component in components if component.reduction)
    score = max(0, min(100, round(additive - reductions)))
    level = _risk_level(score)
    return ExplainableRiskScore(
        score=score,
        level=level,
        components=components,
        formula="final score = min(100, additive contextual components - compensating-control reductions)",
        explanation=f"Contextual risk is {level.value} ({score}/100), driven by CVSS, Internet exposure, IAM linkage and downstream access.",
    )


def _risk_level(score: int) -> RiskLevel:
    if score >= 85:
        return RiskLevel.CRITICAL
    if score >= 65:
        return RiskLevel.HIGH
    if score >= 35:
        return RiskLevel.MEDIUM
    return RiskLevel.LOW
