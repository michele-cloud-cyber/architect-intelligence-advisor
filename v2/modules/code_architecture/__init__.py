"""V3 static Terraform-to-architecture advisory module."""

from .finops import estimate_portfolio
from .intelligence import detect_changes
from .models import AnalysisBundle, ArchitectureResource, Finding, FinOpsEstimate
from .parser import analyze_terraform, simulate_remediation
from .security import InputSecurityError, InputSecurityGateway

__all__ = ["AnalysisBundle", "ArchitectureResource", "Finding", "FinOpsEstimate", "InputSecurityError", "InputSecurityGateway", "analyze_terraform", "simulate_remediation", "estimate_portfolio", "detect_changes"]
