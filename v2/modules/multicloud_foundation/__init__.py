"""Provider-neutral foundation for the adaptive multi-cloud platform."""

from .adapters import AwsDemoAdapter, AzureDemoAdapter, GcpDemoAdapter, adapter_registry
from .governance import GovernanceControlPlane
from .history import LocalScenarioHistory
from .models import (
    CloudResource, CloudResourceModel, ControlRecord, DataSource, EvidenceMode,
    GovernanceDecision, OperationalLevel, PluginManifest, Provider, ScenarioSnapshot,
)
from .orchestrator import MultiCloudOrchestrator
from .plugins import PluginRegistry

__all__ = [
    "AwsDemoAdapter", "AzureDemoAdapter", "GcpDemoAdapter", "adapter_registry",
    "GovernanceControlPlane", "LocalScenarioHistory", "CloudResource",
    "CloudResourceModel", "ControlRecord", "DataSource", "EvidenceMode",
    "GovernanceDecision", "OperationalLevel", "PluginManifest", "Provider",
    "ScenarioSnapshot", "MultiCloudOrchestrator", "PluginRegistry",
]
