"""Evidence enrichment and deterministic fingerprinting for Security Cases."""

from __future__ import annotations

import hashlib
import json
from dataclasses import replace
from typing import Iterable

from v2.modules.security_findings.models import SecurityEvidence, SecurityFinding


def lock_evidence(findings: Iterable[SecurityFinding], case_id: str) -> tuple[SecurityEvidence, ...]:
    """Bind source evidence to a case without retaining secrets or raw scanner data."""

    locked: list[SecurityEvidence] = []
    for finding in findings:
        for evidence in finding.evidence:
            enriched = replace(
                evidence,
                source=finding.source,
                finding_id=finding.finding_id,
                resource_id=finding.cloud_resource_arn or finding.asset_id,
                account_id=finding.cloud_account_id,
                region=finding.cloud_region,
                observed_value=evidence.observed_value or _observed_value(finding),
                case_id=case_id,
                reliability=min(1.0, max(0.0, finding.confidence)),
            )
            locked.append(replace(enriched, fingerprint=evidence_fingerprint(enriched)))
    return tuple(locked)


def evidence_fingerprint(evidence: SecurityEvidence) -> str:
    """Return a repeatable SHA-256 fingerprint of non-sensitive evidence fields."""

    payload = {
        "source": evidence.source.value,
        "finding_id": evidence.finding_id,
        "resource_id": evidence.resource_id,
        "source_reference": evidence.source_reference,
        "observed_value": evidence.observed_value,
        "collected_at": evidence.collected_at.isoformat(),
    }
    return hashlib.sha256(json.dumps(payload, sort_keys=True).encode("utf-8")).hexdigest()


def _observed_value(finding: SecurityFinding) -> str:
    endpoint = f"{finding.ip_address or finding.hostname or finding.asset_id}:{finding.port or 'n/a'}"
    return f"{finding.service or finding.category} observed on {endpoint}"
