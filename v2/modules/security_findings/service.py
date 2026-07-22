"""Application-neutral builder for deterministic demo investigative dossiers."""

from __future__ import annotations

from datetime import datetime
from uuid import NAMESPACE_URL, uuid5

from v2.modules.security_findings.attack_path import build_possible_attack_path
from v2.modules.security_findings.case_id import allocate_case_id
from v2.modules.security_findings.correlation import correlate_findings
from v2.modules.security_findings.demo import build_demo_findings
from v2.modules.security_findings.evidence_locker import lock_evidence
from v2.modules.security_findings.models import CaseStatus, SecurityCase, SecuritySeverity
from v2.modules.security_findings.risk import calculate_risk
from v2.modules.security_findings.storytelling import build_attack_story
from v2.modules.security_findings.timeline import build_case_timeline


def build_demo_security_case(existing_case_ids: tuple[str, ...] = ()) -> SecurityCase:
    """Build a complete local dossier without persistence, network, or AI calls."""

    findings = build_demo_findings()
    created_at = min(item.timestamp for item in findings)
    case_id = allocate_case_id(existing_case_ids, created_at)
    correlations = correlate_findings(findings)
    evidence = lock_evidence(findings, case_id)
    risk = calculate_risk(findings)
    attack_path = build_possible_attack_path(findings, correlations)
    confidence = round(sum(item.confidence_score for item in correlations) / len(correlations)) if correlations else 0
    case = SecurityCase(
        case_id=case_id,
        case_uuid=uuid5(NAMESPACE_URL, f"architect-advisor/security-findings/{case_id}"),
        created_at=created_at,
        status=CaseStatus.NEW,
        severity=SecuritySeverity.CRITICAL,
        finding_ids=tuple(item.finding_id for item in findings),
        asset_ids=tuple(sorted({item.asset_id for item in findings})),
        correlated_vulnerabilities=tuple(sorted({cve for item in findings for cve in item.cves})),
        evidence=evidence,
        attack_path=attack_path,
        remediation=(
            "Restrict public access to the affected HTTPS endpoint.",
            "Patch or replace the vulnerable Apache HTTP Server version.",
            "Review and reduce DemoWebInstanceRole permissions, especially S3 access.",
        ),
        title="Possible Internet-to-S3 compromise path through exposed EC2 workload",
        description="Demo-only dossier correlating Internet exposure, a vulnerable web service and an IAM-linked downstream access path.",
        confidence_score=confidence,
        first_detected=min(item.timestamp for item in findings),
        last_observed=max(item.timestamp for item in findings),
        landing_zone="Demo Landing Zone",
        cloud_account_id=findings[0].cloud_account_id,
        cloud_region=findings[0].cloud_region,
        resource_arns=tuple(sorted({item.cloud_resource_arn for item in findings if item.cloud_resource_arn})),
        findings=findings,
        correlations=correlations,
        risk=risk,
        technical_impact="Potential remote service exploitation followed by role abuse and access to a downstream S3 resource.",
        business_impact="Potential exposure or unauthorized modification of Landing Zone artifacts; no compromise is confirmed.",
    )
    timeline = build_case_timeline(case, findings)
    case = SecurityCase(**{**case.__dict__, "timeline": timeline})
    return SecurityCase(**{**case.__dict__, "attack_story": build_attack_story(case)})
