"""Common Cloud Resource Model; contains no provider SDK dependencies."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any


class Provider(str, Enum):
    AWS = "AWS"
    AZURE = "Azure"
    GCP = "GCP"
    ON_PREMISES = "On-premises"
    THIRD_PARTY = "Third-party"


class EvidenceMode(str, Enum):
    DEMO = "Demo"
    SIMULATION = "Simulation"
    READ_ONLY = "Read-only"
    LIVE = "Live"


class DataSource(str, Enum):
    DEMO = "demo"
    JSON_YAML = "json-yaml"
    TERRAFORM_IMPORT = "terraform-import"
    READ_ONLY_API = "read-only-api"
    CMDB = "cmdb"
    SECURITY = "security-tool"
    FINOPS = "finops"
    THIRD_PARTY = "third-party"


class OperationalLevel(str, Enum):
    CONSULT = "consult"
    SIMULATE = "simulate"
    GENERATE = "generate-code"
    TEST = "test"
    PLAN = "plan"
    APPROVE = "approve"
    CONTROLLED_APPLY = "controlled-apply"


@dataclass(frozen=True)
class CloudResource:
    global_id: str
    provider: Provider
    organization: str
    scope: str
    environment: str
    region: str
    domain: str
    resource_type: str
    name: str
    current: dict[str, Any]
    desired: dict[str, Any]
    classification: str = "Internal"
    dependencies: tuple[str, ...] = ()
    monthly_cost: float = 0.0


@dataclass(frozen=True)
class ControlRecord:
    global_id: str
    provider: Provider
    service: str
    category: str
    observed: Any
    desired: Any
    rule: str
    weight: int
    risk: str
    likelihood: int
    impact: int
    evidence: str
    confidence: int
    remediation: str
    dependencies: tuple[str, ...]
    terraform_mapping: str
    policy_mapping: str
    test_mapping: str
    rollback: str
    approval_status: str = "not-requested"


@dataclass(frozen=True)
class CloudResourceModel:
    model_version: str
    evidence_mode: EvidenceMode
    source: DataSource
    captured_at: str
    resources: tuple[CloudResource, ...]
    controls: tuple[ControlRecord, ...]
    metadata: dict[str, Any] = field(default_factory=dict)

    @staticmethod
    def create(resources: tuple[CloudResource, ...], controls: tuple[ControlRecord, ...], source: DataSource = DataSource.DEMO) -> "CloudResourceModel":
        return CloudResourceModel("1.0", EvidenceMode.DEMO, source, datetime.now(timezone.utc).isoformat(), resources, controls, {"synthetic": True})


@dataclass(frozen=True)
class ScenarioSnapshot:
    scenario_id: str
    name: str
    created_at: str
    author: str
    rationale: str
    current: CloudResourceModel
    desired: CloudResourceModel
    scores: dict[str, int]
    findings: tuple[str, ...]
    approval_status: str = "draft"


@dataclass(frozen=True)
class PluginManifest:
    name: str
    version: str
    capabilities: tuple[str, ...]
    data_read: tuple[str, ...]
    data_written: tuple[str, ...]
    permissions: tuple[str, ...]
    providers: tuple[Provider, ...]
    input_schema: dict[str, str]
    output_schema: dict[str, str]
    timeout_seconds: int
    error_handling: str
    audit_enabled: bool
    trust_status: str


@dataclass(frozen=True)
class GovernanceDecision:
    allowed: bool
    level: OperationalLevel
    reasons: tuple[str, ...]
    required_approvals: tuple[str, ...] = ()
