"""Provider-neutral V3 architecture and advisory records."""

from __future__ import annotations
from dataclasses import dataclass


@dataclass(frozen=True)
class ArchitectureResource:
    resource_id: str; provider: str; file: str; resource_type: str; name: str
    category: str; code: str; dependencies: tuple[str, ...]; flows: tuple[str, ...]
    iam_trust: tuple[str, ...]; current_state: str; desired_state: str
    blast_radius: str; monthly_cost_demo: float | None; confidence: int


@dataclass(frozen=True)
class Finding:
    finding_id: str; provider: str; file: str; resource_id: str; category: str
    severity: str; likelihood: int; impact: int; confidence: int; evidence: str
    rule: str; dependencies: tuple[str, ...]; remediation: str
    terraform_mapping: str; test: str; residual_risk: str


@dataclass(frozen=True)
class FinOpsEstimate:
    resource_id: str; current_monthly: float | None; projected_monthly: float | None
    projected_annual: float | None; one_time: float | None; direct: float | None
    indirect: float | None; prudent: float | None; likely: float | None
    maximum: float | None; budget: float | None; new_total: float | None
    overrun: float | None; required_budget_increase: float | None
    cheaper_alternatives: tuple[str, ...]; confidence: int; assumptions: tuple[str, ...]


@dataclass(frozen=True)
class AnalysisBundle:
    resources: tuple[ArchitectureResource, ...]; findings: tuple[Finding, ...]
    finops: tuple[FinOpsEstimate, ...]; maturity: int; source_files: tuple[str, ...]
    provider: str; environment: str; state_kind: str; warnings: tuple[str, ...]


@dataclass(frozen=True)
class RemediationSimulation:
    original_code: str; proposed_code: str; diff: str; selected_findings: tuple[str, ...]
    risk_before: int; risk_after: int; monthly_before: float | None
    monthly_after: float | None; eliminated: tuple[str, ...]; residual: tuple[str, ...]
    new_risks: tuple[str, ...]; regressions: tuple[str, ...]; tests: tuple[str, ...]
    rollback: str
