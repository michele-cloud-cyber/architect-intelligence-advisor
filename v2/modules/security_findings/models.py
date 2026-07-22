"""Typed, source-neutral contracts for Security Findings investigative dossiers."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from typing import Any
from uuid import UUID


class SecuritySource(StrEnum):
    DEMO = "demo"
    NMAP = "nmap"
    NESSUS = "nessus"
    OPENVAS = "openvas"
    AWS_SECURITY_HUB = "aws_security_hub"
    AMAZON_INSPECTOR = "amazon_inspector"
    MICROSOFT_DEFENDER = "microsoft_defender"
    JSON = "json"
    CSV = "csv"


class SecuritySeverity(StrEnum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFORMATIONAL = "informational"


class CaseStatus(StrEnum):
    NEW = "new"
    TRIAGED = "triaged"
    INVESTIGATING = "investigating"
    REMEDIATION_IN_PROGRESS = "remediation_in_progress"
    MITIGATED = "mitigated"
    MONITORING = "monitoring"
    RESOLVED = "resolved"
    ACCEPTED_RISK = "accepted_risk"
    FALSE_POSITIVE = "false_positive"
    OPEN = "new"  # Compatibility alias for the initial Phase 1 contract.
    CLOSED = "resolved"  # Compatibility alias for the initial Phase 1 contract.


class CorrelationLevel(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class RiskLevel(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass(frozen=True)
class SecurityEvidence:
    """A non-sensitive, traceable technical observation.

    ``fingerprint`` is deterministic and lets a dossier prove which exact demo
    observation supported a correlation without storing secrets or credentials.
    """

    evidence_id: str
    description: str
    source_reference: str
    collected_at: datetime
    source: SecuritySource = SecuritySource.DEMO
    finding_id: str = ""
    resource_id: str = ""
    account_id: str | None = None
    region: str | None = None
    observed_value: str = ""
    case_id: str | None = None
    reliability: float = 0.5
    fingerprint: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "evidence_id": self.evidence_id,
            "description": self.description,
            "source_reference": self.source_reference,
            "collected_at": self.collected_at.isoformat(),
            "source": self.source.value,
            "finding_id": self.finding_id,
            "resource_id": self.resource_id,
            "account_id": self.account_id,
            "region": self.region,
            "observed_value": self.observed_value,
            "case_id": self.case_id,
            "reliability": self.reliability,
            "fingerprint": self.fingerprint,
        }

    @classmethod
    def from_dict(cls, value: dict[str, Any]) -> SecurityEvidence:
        return cls(
            evidence_id=str(value["evidence_id"]),
            description=str(value["description"]),
            source_reference=str(value["source_reference"]),
            collected_at=datetime.fromisoformat(str(value["collected_at"])),
            source=SecuritySource(str(value.get("source", SecuritySource.DEMO))),
            finding_id=str(value.get("finding_id", "")),
            resource_id=str(value.get("resource_id", "")),
            account_id=_optional_string(value.get("account_id")),
            region=_optional_string(value.get("region")),
            observed_value=str(value.get("observed_value", "")),
            case_id=_optional_string(value.get("case_id")),
            reliability=float(value.get("reliability", 0.5)),
            fingerprint=str(value.get("fingerprint", "")),
        )


@dataclass(frozen=True)
class SecurityFinding:
    """Normalized scanner or cloud-security finding."""

    finding_id: str
    source: SecuritySource
    timestamp: datetime
    severity: SecuritySeverity
    confidence: float
    category: str
    asset_id: str
    operating_system: str | None = None
    hostname: str | None = None
    ip_address: str | None = None
    port: int | None = None
    protocol: str | None = None
    service: str | None = None
    cvss: float | None = None
    cves: tuple[str, ...] = ()
    cwes: tuple[str, ...] = ()
    mitre_attack: tuple[str, ...] = ()
    evidence: tuple[SecurityEvidence, ...] = ()
    cloud_account_id: str | None = None
    cloud_region: str | None = None
    cloud_resource_arn: str | None = None
    subnet_id: str | None = None
    internet_exposed: bool = False
    exploit_available: bool = False
    identity_reference: str | None = None
    downstream_resources: tuple[str, ...] = ()
    asset_criticality: float = 0.5

    def to_dict(self) -> dict[str, Any]:
        return {
            "finding_id": self.finding_id,
            "source": self.source.value,
            "timestamp": self.timestamp.isoformat(),
            "severity": self.severity.value,
            "confidence": self.confidence,
            "category": self.category,
            "asset_id": self.asset_id,
            "operating_system": self.operating_system,
            "hostname": self.hostname,
            "ip_address": self.ip_address,
            "port": self.port,
            "protocol": self.protocol,
            "service": self.service,
            "cvss": self.cvss,
            "cves": list(self.cves),
            "cwes": list(self.cwes),
            "mitre_attack": list(self.mitre_attack),
            "evidence": [item.to_dict() for item in self.evidence],
            "cloud_account_id": self.cloud_account_id,
            "cloud_region": self.cloud_region,
            "cloud_resource_arn": self.cloud_resource_arn,
            "subnet_id": self.subnet_id,
            "internet_exposed": self.internet_exposed,
            "exploit_available": self.exploit_available,
            "identity_reference": self.identity_reference,
            "downstream_resources": list(self.downstream_resources),
            "asset_criticality": self.asset_criticality,
        }

    @classmethod
    def from_dict(cls, value: dict[str, Any]) -> SecurityFinding:
        return cls(
            finding_id=str(value["finding_id"]),
            source=SecuritySource(str(value["source"])),
            timestamp=datetime.fromisoformat(str(value["timestamp"])),
            severity=SecuritySeverity(str(value["severity"])),
            confidence=float(value["confidence"]),
            category=str(value["category"]),
            asset_id=str(value["asset_id"]),
            operating_system=_optional_string(value.get("operating_system")),
            hostname=_optional_string(value.get("hostname")),
            ip_address=_optional_string(value.get("ip_address")),
            port=_optional_int(value.get("port")),
            protocol=_optional_string(value.get("protocol")),
            service=_optional_string(value.get("service")),
            cvss=_optional_float(value.get("cvss")),
            cves=tuple(str(item) for item in value.get("cves", [])),
            cwes=tuple(str(item) for item in value.get("cwes", [])),
            mitre_attack=tuple(str(item) for item in value.get("mitre_attack", [])),
            evidence=tuple(SecurityEvidence.from_dict(item) for item in value.get("evidence", [])),
            cloud_account_id=_optional_string(value.get("cloud_account_id")),
            cloud_region=_optional_string(value.get("cloud_region")),
            cloud_resource_arn=_optional_string(value.get("cloud_resource_arn")),
            subnet_id=_optional_string(value.get("subnet_id")),
            internet_exposed=bool(value.get("internet_exposed", False)),
            exploit_available=bool(value.get("exploit_available", False)),
            identity_reference=_optional_string(value.get("identity_reference")),
            downstream_resources=tuple(str(item) for item in value.get("downstream_resources", [])),
            asset_criticality=float(value.get("asset_criticality", 0.5)),
        )


@dataclass(frozen=True)
class FindingCorrelation:
    """Evidence-based relation between findings, never presented as certainty."""

    finding_ids: tuple[str, str]
    confidence_score: int
    level: CorrelationLevel
    evidence_ids: tuple[str, ...]
    explanation: str
    label: str = "possible attack path"


@dataclass(frozen=True)
class RiskComponent:
    name: str
    score: float
    maximum: float
    rationale: str
    reduction: bool = False


@dataclass(frozen=True)
class ExplainableRiskScore:
    score: int
    level: RiskLevel
    components: tuple[RiskComponent, ...]
    formula: str
    explanation: str


@dataclass(frozen=True)
class AttackPath:
    label: str
    steps: tuple[str, ...]
    confidence_score: int
    evidence_ids: tuple[str, ...]
    disclaimer: str = "Possible attack path inferred from correlated evidence; not a confirmed compromise."


@dataclass(frozen=True)
class SecurityTimelineEvent:
    event_id: str
    timestamp: datetime
    event_type: str
    description: str
    source: SecuritySource
    status_change: str | None = None
    previous_risk_score: int | None = None
    new_risk_score: int | None = None


@dataclass(frozen=True)
class SecurityCase:
    """An immutable, self-contained investigative dossier."""

    case_id: str
    case_uuid: UUID
    created_at: datetime
    status: CaseStatus
    severity: SecuritySeverity
    finding_ids: tuple[str, ...]
    asset_ids: tuple[str, ...]
    correlated_vulnerabilities: tuple[str, ...]
    evidence: tuple[SecurityEvidence, ...] = ()
    attack_path: AttackPath | None = None
    remediation: tuple[str, ...] = ()
    metadata: dict[str, str] = field(default_factory=dict)
    title: str = ""
    description: str = ""
    confidence_score: int = 0
    first_detected: datetime | None = None
    last_observed: datetime | None = None
    landing_zone: str | None = None
    cloud_account_id: str | None = None
    cloud_region: str | None = None
    resource_arns: tuple[str, ...] = ()
    findings: tuple[SecurityFinding, ...] = ()
    correlations: tuple[FindingCorrelation, ...] = ()
    risk: ExplainableRiskScore | None = None
    technical_impact: str = ""
    business_impact: str = ""
    assigned_owner: str | None = None
    timeline: tuple[SecurityTimelineEvent, ...] = ()
    attack_story: str = ""


def _optional_string(value: Any) -> str | None:
    return str(value) if value is not None else None


def _optional_int(value: Any) -> int | None:
    return int(value) if value is not None else None


def _optional_float(value: Any) -> float | None:
    return float(value) if value is not None else None
