"""Security Findings domain module for Architect Advisor V2.

The package is intentionally independent from the V1 assessment pipeline and is
accessed by presentation clients only through ``DashboardService`` once wired.
"""

from v2.modules.security_findings.models import (
    CaseStatus,
    SecurityCase,
    SecurityEvidence,
    SecurityFinding,
    SecuritySeverity,
    SecuritySource,
)
from v2.modules.security_findings.repository import SecurityFindingsRepository
from v2.modules.security_findings.demo import build_demo_findings
from v2.modules.security_findings.importers.registry import default_importer_registry
from v2.modules.security_findings.service import build_demo_security_case

__all__ = [
    "CaseStatus",
    "SecurityCase",
    "SecurityEvidence",
    "SecurityFinding",
    "SecurityFindingsRepository",
    "SecuritySeverity",
    "SecuritySource",
    "build_demo_findings",
    "default_importer_registry",
    "build_demo_security_case",
]
