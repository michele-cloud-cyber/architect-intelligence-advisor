"""Source-neutral validation and normalization for security findings."""

from __future__ import annotations

from dataclasses import replace

from v2.modules.security_findings.models import SecurityFinding


def normalize_finding(finding: SecurityFinding) -> SecurityFinding:
    """Return a canonical finding without discarding source evidence.

    Importers own source parsing; this layer owns only the stable domain shape.
    It is intentionally pure so it can be shared by future API and batch clients.
    """

    confidence = min(1.0, max(0.0, finding.confidence))
    cvss = None if finding.cvss is None else min(10.0, max(0.0, finding.cvss))
    port = None if finding.port is None else max(0, min(65535, finding.port))
    return replace(
        finding,
        finding_id=finding.finding_id.strip(),
        category=finding.category.strip(),
        asset_id=finding.asset_id.strip(),
        hostname=_clean_optional(finding.hostname),
        ip_address=_clean_optional(finding.ip_address),
        protocol=_clean_optional(finding.protocol, lowercase=True),
        service=_clean_optional(finding.service, lowercase=True),
        cvss=cvss,
        confidence=confidence,
        port=port,
        cves=tuple(sorted({item.strip().upper() for item in finding.cves if item.strip()})),
        cwes=tuple(sorted({item.strip().upper() for item in finding.cwes if item.strip()})),
        mitre_attack=tuple(sorted({item.strip().upper() for item in finding.mitre_attack if item.strip()})),
    )


def _clean_optional(value: str | None, *, lowercase: bool = False) -> str | None:
    if value is None:
        return None
    cleaned = value.strip()
    return cleaned.lower() if lowercase else cleaned
