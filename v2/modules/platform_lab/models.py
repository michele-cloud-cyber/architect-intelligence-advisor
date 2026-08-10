"""Shared, presentation-independent contracts for Platform Lab phase one."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class OperatingMode(StrEnum):
    DEMO = "Demo"
    SIMULATION = "Simulation"
    AWS_READ_ONLY = "AWS Read-only"


class ResultStatus(StrEnum):
    CORRECT = "Correct"
    IMPROVABLE = "Improvable"
    MEDIUM_RISK = "Medium risk"
    HIGH_RISK = "High risk"
    INSUFFICIENT = "Insufficient data"


@dataclass(frozen=True)
class ProjectDefinition:
    name: str
    objective: str
    description: str
    services: tuple[str, ...]
    accounts: tuple[str, ...]
    environments: tuple[str, ...]
    regions: tuple[str, ...]
    identities: str
    data_classification: str
    network_requirements: str
    security_requirements: str
    compliance: str
    availability: str
    backup_dr: str
    budget: str
    rto_hours: int
    rpo_hours: int
    constraints: str
    mode: OperatingMode
    configuration: dict[str, bool | str] = field(default_factory=dict)


@dataclass(frozen=True)
class ControlDefinition:
    control_id: str
    category: str
    description: str
    input_key: str
    weight: int
    remediation: str
    terraform_mapping: str
    test_id: str
    estimated_monthly_cost: str = "$0"


@dataclass(frozen=True)
class ControlResult:
    definition: ControlDefinition
    current_value: str
    score: int
    status: ResultStatus
    severity: str
    rationale: str
    confidence: int


@dataclass(frozen=True)
class ProjectAnalysis:
    missing_information: tuple[str, ...]
    contradictions: tuple[str, ...]
    risks: tuple[str, ...]
    dependencies: tuple[str, ...]
    improvements: tuple[str, ...]


@dataclass(frozen=True)
class SimulationResult:
    before_scores: dict[str, int | None]
    after_scores: dict[str, int | None]
    before_overall: int
    after_overall: int
    absolute_delta: int
    percentage_delta: float
    eliminated_risks: tuple[str, ...]
    residual_risks: tuple[str, ...]
    new_risks: tuple[str, ...]
    dependencies: tuple[str, ...]
    operational_impact: str
    estimated_cost: str
    confidence: int
    contributions: tuple[dict[str, Any], ...]
    proposed_configuration: dict[str, bool | str]


@dataclass(frozen=True)
class TerraformPackage:
    files: dict[str, str]
    decision_summary: dict[str, Any]


@dataclass(frozen=True)
class ValidationResult:
    check: str
    command: str
    status: str
    result: str
    rationale: str
