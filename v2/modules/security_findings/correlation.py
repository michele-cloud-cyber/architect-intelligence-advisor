"""Explainable, deterministic correlation of normalized Security Findings."""

from __future__ import annotations

from itertools import combinations
from typing import Iterable

from v2.modules.security_findings.models import CorrelationLevel, FindingCorrelation, SecurityFinding


def correlate_findings(findings: Iterable[SecurityFinding]) -> tuple[FindingCorrelation, ...]:
    """Build only evidence-based, explicitly possible relationships."""

    result = []
    for left, right in combinations(sorted(findings, key=lambda item: item.finding_id), 2):
        reasons, score = _correlation_reasons(left, right)
        if not reasons:
            continue
        result.append(
            FindingCorrelation(
                finding_ids=(left.finding_id, right.finding_id),
                confidence_score=min(score, 100),
                level=_level_for_score(score),
                evidence_ids=tuple(item.evidence_id for item in (*left.evidence, *right.evidence)),
                explanation="; ".join(reasons) + ". This is a possible attack path, not a confirmed compromise.",
            )
        )
    return tuple(result)


def _correlation_reasons(left: SecurityFinding, right: SecurityFinding) -> tuple[list[str], int]:
    reasons: list[str] = []
    score = 0
    if left.asset_id == right.asset_id:
        reasons.append("same asset")
        score += 30
    if left.hostname and left.hostname == right.hostname:
        reasons.append("same hostname")
        score += 10
    if left.ip_address and left.ip_address == right.ip_address:
        reasons.append("same IP address")
        score += 10
    if left.subnet_id and left.subnet_id == right.subnet_id:
        reasons.append("same subnet")
        score += 10
    if left.port is not None and left.port == right.port:
        reasons.append("same exposed port")
        score += 10
    if left.service and left.service == right.service:
        reasons.append("same service")
        score += 10
    if set(left.cves) & set(right.cves):
        reasons.append("shared CVE")
        score += 20
    if set(left.cwes) & set(right.cwes):
        reasons.append("shared CWE family")
        score += 10
    if left.internet_exposed and right.internet_exposed:
        reasons.append("shared Internet exposure")
        score += 10
    if left.identity_reference and left.identity_reference == right.identity_reference:
        reasons.append("same IAM identity or role")
        score += 10
    if set(left.mitre_attack) != set(right.mitre_attack) and set(left.mitre_attack) & {"T1190", "T1068", "T1078"} and set(right.mitre_attack) & {"T1190", "T1068", "T1078"}:
        reasons.append("complementary MITRE techniques indicate a possible attack chain")
        score += 15
    return reasons, score


def _level_for_score(score: int) -> CorrelationLevel:
    if score >= 70:
        return CorrelationLevel.HIGH
    if score >= 40:
        return CorrelationLevel.MEDIUM
    return CorrelationLevel.LOW
