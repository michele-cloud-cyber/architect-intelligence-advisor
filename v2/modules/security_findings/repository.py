"""Local persistence boundary for Security Findings dossiers.

It never reads or writes V1 history snapshots.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any
from uuid import UUID

from v2.modules.security_findings.models import (
    AttackPath,
    CaseStatus,
    CorrelationLevel,
    ExplainableRiskScore,
    FindingCorrelation,
    RiskComponent,
    RiskLevel,
    SecurityCase,
    SecurityEvidence,
    SecurityFinding,
    SecuritySeverity,
    SecuritySource,
    SecurityTimelineEvent,
)


class SecurityFindingsRepository:
    """Persist dossiers beneath an isolated module-owned directory."""

    def __init__(self, project_root: Path):
        self._cases_directory = project_root / "history" / "security_findings" / "cases"

    def list_case_ids(self) -> tuple[str, ...]:
        if not self._cases_directory.exists():
            return ()
        return tuple(sorted(path.stem for path in self._cases_directory.glob("*.json")))

    def save_case(self, case: SecurityCase) -> Path:
        self._cases_directory.mkdir(parents=True, exist_ok=True)
        path = self._cases_directory / f"{case.case_id}.json"
        temporary_path = path.with_suffix(".tmp")
        temporary_path.write_text(json.dumps(_case_to_dict(case), indent=2, sort_keys=True), encoding="utf-8")
        temporary_path.replace(path)
        return path

    def get_case(self, case_id: str) -> SecurityCase | None:
        path = self._cases_directory / f"{case_id}.json"
        if not path.exists():
            return None
        return _case_from_dict(json.loads(path.read_text(encoding="utf-8")))


def _case_to_dict(case: SecurityCase) -> dict[str, Any]:
    return {
        "case_id": case.case_id,
        "case_uuid": str(case.case_uuid),
        "created_at": case.created_at.isoformat(),
        "status": case.status.value,
        "severity": case.severity.value,
        "finding_ids": list(case.finding_ids),
        "asset_ids": list(case.asset_ids),
        "correlated_vulnerabilities": list(case.correlated_vulnerabilities),
        "evidence": [item.to_dict() for item in case.evidence],
        "attack_path": _attack_path_to_dict(case.attack_path),
        "remediation": list(case.remediation),
        "metadata": case.metadata,
        "title": case.title,
        "description": case.description,
        "confidence_score": case.confidence_score,
        "first_detected": _datetime_to_string(case.first_detected),
        "last_observed": _datetime_to_string(case.last_observed),
        "landing_zone": case.landing_zone,
        "cloud_account_id": case.cloud_account_id,
        "cloud_region": case.cloud_region,
        "resource_arns": list(case.resource_arns),
        "findings": [item.to_dict() for item in case.findings],
        "correlations": [_correlation_to_dict(item) for item in case.correlations],
        "risk": _risk_to_dict(case.risk),
        "technical_impact": case.technical_impact,
        "business_impact": case.business_impact,
        "assigned_owner": case.assigned_owner,
        "timeline": [_timeline_to_dict(item) for item in case.timeline],
        "attack_story": case.attack_story,
    }


def _case_from_dict(value: dict[str, Any]) -> SecurityCase:
    return SecurityCase(
        case_id=str(value["case_id"]),
        case_uuid=UUID(str(value["case_uuid"])),
        created_at=datetime.fromisoformat(str(value["created_at"])),
        status=CaseStatus(str(value["status"])),
        severity=SecuritySeverity(str(value["severity"])),
        finding_ids=tuple(str(item) for item in value.get("finding_ids", [])),
        asset_ids=tuple(str(item) for item in value.get("asset_ids", [])),
        correlated_vulnerabilities=tuple(str(item) for item in value.get("correlated_vulnerabilities", [])),
        evidence=tuple(SecurityEvidence.from_dict(item) for item in value.get("evidence", [])),
        attack_path=_attack_path_from_dict(value.get("attack_path")),
        remediation=tuple(str(item) for item in value.get("remediation", [])),
        metadata={str(key): str(item) for key, item in value.get("metadata", {}).items()},
        title=str(value.get("title", "")),
        description=str(value.get("description", "")),
        confidence_score=int(value.get("confidence_score", 0)),
        first_detected=_datetime_from_string(value.get("first_detected")),
        last_observed=_datetime_from_string(value.get("last_observed")),
        landing_zone=_string_or_none(value.get("landing_zone")),
        cloud_account_id=_string_or_none(value.get("cloud_account_id")),
        cloud_region=_string_or_none(value.get("cloud_region")),
        resource_arns=tuple(str(item) for item in value.get("resource_arns", [])),
        findings=tuple(SecurityFinding.from_dict(item) for item in value.get("findings", [])),
        correlations=tuple(_correlation_from_dict(item) for item in value.get("correlations", [])),
        risk=_risk_from_dict(value.get("risk")),
        technical_impact=str(value.get("technical_impact", "")),
        business_impact=str(value.get("business_impact", "")),
        assigned_owner=_string_or_none(value.get("assigned_owner")),
        timeline=tuple(_timeline_from_dict(item) for item in value.get("timeline", [])),
        attack_story=str(value.get("attack_story", "")),
    )


def _attack_path_to_dict(value: AttackPath | None) -> dict[str, Any] | None:
    if value is None:
        return None
    return {"label": value.label, "steps": list(value.steps), "confidence_score": value.confidence_score, "evidence_ids": list(value.evidence_ids), "disclaimer": value.disclaimer}


def _attack_path_from_dict(value: dict[str, Any] | None) -> AttackPath | None:
    if not value:
        return None
    return AttackPath(str(value["label"]), tuple(str(item) for item in value.get("steps", [])), int(value["confidence_score"]), tuple(str(item) for item in value.get("evidence_ids", [])), str(value.get("disclaimer", "Possible attack path inferred from correlated evidence; not a confirmed compromise.")))


def _correlation_to_dict(value: FindingCorrelation) -> dict[str, Any]:
    return {"finding_ids": list(value.finding_ids), "confidence_score": value.confidence_score, "level": value.level.value, "evidence_ids": list(value.evidence_ids), "explanation": value.explanation, "label": value.label}


def _correlation_from_dict(value: dict[str, Any]) -> FindingCorrelation:
    finding_ids = tuple(str(item) for item in value["finding_ids"])
    return FindingCorrelation((finding_ids[0], finding_ids[1]), int(value["confidence_score"]), CorrelationLevel(str(value["level"])), tuple(str(item) for item in value.get("evidence_ids", [])), str(value["explanation"]), str(value.get("label", "possible attack path")))


def _risk_to_dict(value: ExplainableRiskScore | None) -> dict[str, Any] | None:
    if value is None:
        return None
    return {"score": value.score, "level": value.level.value, "components": [{"name": item.name, "score": item.score, "maximum": item.maximum, "rationale": item.rationale, "reduction": item.reduction} for item in value.components], "formula": value.formula, "explanation": value.explanation}


def _risk_from_dict(value: dict[str, Any] | None) -> ExplainableRiskScore | None:
    if not value:
        return None
    return ExplainableRiskScore(int(value["score"]), RiskLevel(str(value["level"])), tuple(RiskComponent(str(item["name"]), float(item["score"]), float(item["maximum"]), str(item["rationale"]), bool(item.get("reduction", False))) for item in value.get("components", [])), str(value["formula"]), str(value["explanation"]))


def _timeline_to_dict(value: SecurityTimelineEvent) -> dict[str, Any]:
    return {"event_id": value.event_id, "timestamp": value.timestamp.isoformat(), "event_type": value.event_type, "description": value.description, "source": value.source.value, "status_change": value.status_change, "previous_risk_score": value.previous_risk_score, "new_risk_score": value.new_risk_score}


def _timeline_from_dict(value: dict[str, Any]) -> SecurityTimelineEvent:
    return SecurityTimelineEvent(str(value["event_id"]), datetime.fromisoformat(str(value["timestamp"])), str(value["event_type"]), str(value["description"]), SecuritySource(str(value["source"])), _string_or_none(value.get("status_change")), _int_or_none(value.get("previous_risk_score")), _int_or_none(value.get("new_risk_score")))


def _datetime_to_string(value: datetime | None) -> str | None:
    return value.isoformat() if value is not None else None


def _datetime_from_string(value: Any) -> datetime | None:
    return datetime.fromisoformat(str(value)) if value is not None else None


def _string_or_none(value: Any) -> str | None:
    return str(value) if value is not None else None


def _int_or_none(value: Any) -> int | None:
    return int(value) if value is not None else None
