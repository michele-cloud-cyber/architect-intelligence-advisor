"""Demo adapter contracts and provider implementations; no network access."""

from __future__ import annotations

from abc import ABC, abstractmethod

from .models import CloudResource, CloudResourceModel, ControlRecord, DataSource, Provider


class CloudAdapter(ABC):
    provider: Provider
    live_connection = False

    @abstractmethod
    def load_demo(self) -> CloudResourceModel: ...

    @abstractmethod
    def validate(self, model: CloudResourceModel) -> tuple[str, ...]: ...

    def _model(self, scope: str, region: str, resource_type: str, service: str) -> CloudResourceModel:
        key = self.provider.value.lower().replace("-", "").replace(" ", "-")
        resource = CloudResource(
            f"crm:{key}:demo:core", self.provider, "Demo Organization", scope,
            "development", region, "data", resource_type, "demo-workload",
            {"encryption": False, "public_access": False},
            {"encryption": True, "public_access": False}, "Confidential", (), 24.0,
        )
        control = ControlRecord(
            f"CTRL-{key.upper()}-001", self.provider, service, "Data Protection",
            False, True, "Encryption at rest must be enabled", 8,
            "Unencrypted data exposure", 3, 4, "synthetic demo value", 45,
            "Enable provider-managed encryption", (), f"{resource_type}.encryption",
            "policy.data.encryption", "contract:test_encryption", "Restore prior setting",
        )
        return CloudResourceModel.create((resource,), (control,), DataSource.DEMO)

    def validate(self, model: CloudResourceModel) -> tuple[str, ...]:
        errors = []
        if model.source is not DataSource.DEMO or not model.metadata.get("synthetic"):
            errors.append("Demo adapter accepts synthetic demo data only")
        if any(resource.provider is not self.provider for resource in model.resources):
            errors.append("Provider boundary violation")
        return tuple(errors)


class AwsDemoAdapter(CloudAdapter):
    provider = Provider.AWS
    def load_demo(self) -> CloudResourceModel:
        return self._model("demo-account", "eu-west-1", "aws_s3_bucket", "S3")


class AzureDemoAdapter(CloudAdapter):
    provider = Provider.AZURE
    def load_demo(self) -> CloudResourceModel:
        return self._model("demo-subscription", "westeurope", "azurerm_storage_account", "Storage")


class GcpDemoAdapter(CloudAdapter):
    provider = Provider.GCP
    def load_demo(self) -> CloudResourceModel:
        return self._model("demo-project", "europe-west1", "google_storage_bucket", "Cloud Storage")


def adapter_registry() -> dict[Provider, CloudAdapter]:
    return {adapter.provider: adapter for adapter in (AwsDemoAdapter(), AzureDemoAdapter(), GcpDemoAdapter())}
