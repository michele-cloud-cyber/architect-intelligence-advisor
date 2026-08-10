"""Public API for the interactive architecture and Terraform lab."""

from v2.modules.platform_lab.models import OperatingMode, ProjectDefinition
from v2.modules.platform_lab.pipeline import github_actions_example
from v2.modules.platform_lab.scoring import analyze_project, evaluate_controls
from v2.modules.platform_lab.simulation import simulate_s3_changes
from v2.modules.platform_lab.terraform import generate_s3_package, package_zip_bytes
from v2.modules.platform_lab.validation import validate_s3_package

__all__ = [
    "OperatingMode",
    "ProjectDefinition",
    "analyze_project",
    "evaluate_controls",
    "simulate_s3_changes",
    "generate_s3_package",
    "package_zip_bytes",
    "validate_s3_package",
    "github_actions_example",
]
