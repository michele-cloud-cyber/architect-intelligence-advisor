"""Fault-isolated coordination primitives for the complete application."""

from .health import HealthStatus, ModuleHealth, probe_modules
from .state import NormalizedAppState, STATE_SCHEMA_VERSION
from .registry import MODULE_REGISTRY, ModuleDefinition, get_module, search_modules

__all__ = ["HealthStatus", "ModuleHealth", "probe_modules", "NormalizedAppState", "STATE_SCHEMA_VERSION", "MODULE_REGISTRY", "ModuleDefinition", "get_module", "search_modules"]
