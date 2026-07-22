"""Possible attack-path construction from demonstrable finding relationships."""

from __future__ import annotations

from typing import Iterable

from v2.modules.security_findings.models import AttackPath, FindingCorrelation, SecurityFinding


def build_possible_attack_path(
    findings: Iterable[SecurityFinding], correlations: Iterable[FindingCorrelation]
) -> AttackPath:
    """Build a conservative path with a clear non-confirmation disclaimer."""

    items = tuple(findings)
    confidence = max((item.confidence_score for item in correlations), default=0)
    evidence_ids = tuple(sorted({evidence.evidence_id for item in items for evidence in item.evidence}))
    entry = next((item for item in items if item.internet_exposed), items[0])
    identity = next((item for item in items if item.identity_reference), None)
    downstream = tuple(sorted({resource for item in items for resource in item.downstream_resources}))
    steps = [
        "Internet",
        f"Open {entry.protocol or 'network'} port {entry.port or 'unknown'} on {entry.asset_id}",
        f"Potentially vulnerable {entry.service or entry.category}",
    ]
    if identity is not None:
        steps.append(f"Possible privilege use through IAM role {identity.identity_reference}")
    steps.append(f"EC2 asset {entry.asset_id}")
    steps.extend(f"Reachable downstream resource {resource}" for resource in downstream)
    steps.append("Landing Zone")
    return AttackPath("possible attack path", tuple(steps), confidence, evidence_ids)
