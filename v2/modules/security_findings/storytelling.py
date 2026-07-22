"""Local deterministic SOC-style narrative generation; no Bedrock dependency."""

from __future__ import annotations

from v2.modules.security_findings.models import SecurityCase


def build_attack_story(case: SecurityCase) -> str:
    """Narrate only dossier evidence and clearly qualify inferred relationships."""

    path = case.attack_path.steps if case.attack_path else ()
    entry = path[1] if len(path) > 1 else "an affected asset"
    downstream = next((step for step in path if step.startswith("Reachable downstream resource")), "no downstream resource evidenced")
    evidence_count = len(case.evidence)
    risk = case.risk.level.value.title() if case.risk else "Unknown"
    return (
        f"A possible compromise chain was identified starting from {entry}. "
        f"The correlated findings indicate vulnerable or exposed services and a possible IAM privilege path. "
        f"The path may reach {downstream}. Correlation is supported by {evidence_count} independent evidence items "
        f"with {case.confidence_score}% confidence. Contextual risk is {risk}. "
        "This is an evidence-based hypothesis, not confirmation of compromise; prioritize remediation and validation."
    )
