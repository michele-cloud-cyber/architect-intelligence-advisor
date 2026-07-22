"""Deterministic demo findings used until scanner ingestion is explicitly enabled."""

from __future__ import annotations

from datetime import datetime, timezone

from v2.modules.security_findings.models import (
    SecurityEvidence,
    SecurityFinding,
    SecuritySeverity,
    SecuritySource,
)
from v2.modules.security_findings.normalization import normalize_finding


def build_demo_findings() -> tuple[SecurityFinding, ...]:
    """Return realistic, non-persisted findings for the Security Findings MVP."""

    observed_at = datetime(2026, 7, 22, 9, 0, tzinfo=timezone.utc)
    public_ec2 = "arn:aws:ec2:eu-south-1:111122223333:instance/i-demo-web-001"
    base = {
        "source": SecuritySource.DEMO,
        "timestamp": observed_at,
        "asset_id": "i-demo-web-001",
        "operating_system": "Amazon Linux 2023",
        "hostname": "demo-web-01",
        "ip_address": "203.0.113.10",
        "cloud_account_id": "111122223333",
        "cloud_region": "eu-south-1",
        "cloud_resource_arn": public_ec2,
        "subnet_id": "subnet-demo-public",
        "internet_exposed": True,
        "identity_reference": "DemoWebInstanceRole",
        "downstream_resources": ("arn:aws:s3:::demo-landing-zone-artifacts",),
        "asset_criticality": 0.8,
    }

    findings = (
        SecurityFinding(
            finding_id="DEMO-NMAP-0001",
            severity=SecuritySeverity.HIGH,
            confidence=0.95,
            category="External exposure",
            port=443,
            protocol="TCP",
            service="Apache HTTP Server",
            cvss=8.1,
            cves=("CVE-2024-38476",),
            cwes=("CWE-200",),
            mitre_attack=("T1190",),
            exploit_available=True,
            evidence=(
                SecurityEvidence(
                    evidence_id="DEMO-EVIDENCE-0001",
                    description="HTTPS listener is publicly reachable on TCP/443.",
                    source_reference="demo://nmap/demo-web-01/443",
                    collected_at=observed_at,
                ),
            ),
            **base,
        ),
        SecurityFinding(
            finding_id="DEMO-NESSUS-0002",
            severity=SecuritySeverity.CRITICAL,
            confidence=0.9,
            category="Vulnerable web service",
            port=443,
            protocol="TCP",
            service="Apache HTTP Server",
            cvss=9.8,
            cves=("CVE-2024-38476",),
            cwes=("CWE-200",),
            mitre_attack=("T1190",),
            exploit_available=True,
            evidence=(
                SecurityEvidence(
                    evidence_id="DEMO-EVIDENCE-0002",
                    description="Scanner identified a vulnerable Apache version on the exposed endpoint.",
                    source_reference="demo://nessus/plugin/0002",
                    collected_at=observed_at,
                ),
            ),
            **base,
        ),
        SecurityFinding(
            finding_id="DEMO-INSPECTOR-0003",
            severity=SecuritySeverity.CRITICAL,
            confidence=0.85,
            category="Privilege escalation path",
            port=None,
            protocol=None,
            service="IAM role",
            cvss=9.1,
            cves=("CVE-2024-38476",),
            cwes=("CWE-269",),
            mitre_attack=("T1068", "T1078"),
            exploit_available=False,
            evidence=(
                SecurityEvidence(
                    evidence_id="DEMO-EVIDENCE-0003",
                    description="EC2 instance role permits broad S3 access in the demo scenario.",
                    source_reference="demo://inspector/i-demo-web-001/role",
                    collected_at=observed_at,
                ),
            ),
            **base,
        ),
    )
    return tuple(normalize_finding(finding) for finding in findings)
