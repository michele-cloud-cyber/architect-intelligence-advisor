"""Chronological internal case timeline generation."""

from __future__ import annotations

from datetime import timedelta
from typing import Iterable

from v2.modules.security_findings.models import SecurityCase, SecurityFinding, SecuritySource, SecurityTimelineEvent


def build_case_timeline(case: SecurityCase, findings: Iterable[SecurityFinding]) -> tuple[SecurityTimelineEvent, ...]:
    """Build an auditable, deterministic timeline for a newly opened demo case."""

    items = tuple(sorted(findings, key=lambda item: (item.timestamp, item.finding_id)))
    if not items:
        return ()
    start = items[0].timestamp
    source = items[0].source
    risk_score = case.risk.score if case.risk else 0
    events = [
        SecurityTimelineEvent("TL-0001", start, "finding_detected", f"Finding {items[0].finding_id} detected.", source),
        SecurityTimelineEvent("TL-0002", start + timedelta(seconds=1), "evidence_acquired", f"{len(case.evidence)} technical evidence items locked for the dossier.", source),
        SecurityTimelineEvent("TL-0003", start + timedelta(seconds=2), "correlation_created", f"{len(case.correlations)} possible finding correlations created.", source),
        SecurityTimelineEvent("TL-0004", start + timedelta(seconds=3), "case_opened", f"Security Case {case.case_id} opened.", SecuritySource.DEMO, status_change="New", previous_risk_score=0, new_risk_score=risk_score),
        SecurityTimelineEvent("TL-0005", start + timedelta(seconds=4), "remediation_proposed", "Priority remediation actions proposed for review.", SecuritySource.DEMO),
    ]
    return tuple(sorted(events, key=lambda item: item.timestamp))
