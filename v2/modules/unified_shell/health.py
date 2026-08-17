"""Lazy health probes: import failures never crash the stable application."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from importlib import import_module


class HealthStatus(str, Enum):
    AVAILABLE = "Available"
    DEGRADED = "Degraded"
    UNAVAILABLE = "Unavailable"


@dataclass(frozen=True)
class ModuleHealth:
    module_id: str
    label: str
    status: HealthStatus
    detail: str


MODULE_PROBES = {
    "stable_lab": ("Laboratorio stabile", "dashboard_v2.components.platform_lab", "render_platform_lab", False),
    "multicloud": ("Foundation multi-cloud", "dashboard_v2.components.multicloud_foundation", "render_multicloud_platform", False),
    "governance": ("Governance e orchestratore", "v2.modules.multicloud_foundation", "GovernanceControlPlane", False),
    "terraform": ("Terraform e validazione", "v2.modules.platform_lab.terraform", "generate_s3_package", False),
    "finops": ("FinOps trasversale", "v2.modules.finops_dashboard", "render_finops", True),
    "security_findings": ("Vulnerability Intelligence", "dashboard_v2.components.security_findings", "render_vulnerability_intelligence", False),
}


def probe_modules(forced_failure: str | None = None) -> tuple[ModuleHealth, ...]:
    health = []
    for module_id, (label, path, attribute, optional) in MODULE_PROBES.items():
        if forced_failure == module_id:
            health.append(ModuleHealth(module_id, label, HealthStatus.UNAVAILABLE, "Guasto simulato e isolato"))
            continue
        try:
            module = import_module(path)
            if not hasattr(module, attribute):
                status = HealthStatus.DEGRADED if optional else HealthStatus.UNAVAILABLE
                health.append(ModuleHealth(module_id, label, status, f"Interfaccia opzionale {attribute} non implementata"))
            else:
                health.append(ModuleHealth(module_id, label, HealthStatus.AVAILABLE, "Interfaccia caricata"))
        except Exception as exc:  # health boundary intentionally catches import failures
            health.append(ModuleHealth(module_id, label, HealthStatus.DEGRADED if optional else HealthStatus.UNAVAILABLE, f"{type(exc).__name__}: {exc}"))
    return tuple(health)
