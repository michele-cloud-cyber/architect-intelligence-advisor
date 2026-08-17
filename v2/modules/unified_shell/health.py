"""Lazy health probes: import failures never crash the stable application."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from importlib import import_module
from .registry import MODULE_REGISTRY


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


def probe_modules(forced_failure: str | None = None) -> tuple[ModuleHealth, ...]:
    health = []
    for definition in MODULE_REGISTRY:
        module_id,label,path,attribute,optional=definition.module_id,definition.name_it,definition.probe_module,definition.probe_attribute,definition.optional
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
