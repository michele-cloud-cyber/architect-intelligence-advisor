"""Restricted coordinator; every action passes through governance."""

from __future__ import annotations

from .adapters import CloudAdapter
from .governance import GovernanceControlPlane
from .history import LocalScenarioHistory
from .models import OperationalLevel, Provider
from .plugins import PluginRegistry


class MultiCloudOrchestrator:
    def __init__(self, adapters: dict[Provider, CloudAdapter], governance: GovernanceControlPlane, history: LocalScenarioHistory, plugins: PluginRegistry):
        self.adapters, self.governance, self.history, self.plugins = adapters, governance, history, plugins

    def overview(self, providers: tuple[Provider, ...]) -> tuple:
        decision = self.governance.authorize(OperationalLevel.CONSULT)
        if not decision.allowed:
            raise PermissionError(decision.reasons)
        models = tuple(self.adapters[provider].load_demo() for provider in providers)
        for model in models:
            errors = self.adapters[model.resources[0].provider].validate(model)
            if errors:
                raise ValueError(errors)
        return models

    def execution_plan(self, providers: tuple[Provider, ...]) -> tuple[dict, ...]:
        steps = []
        for level in OperationalLevel:
            decision = self.governance.authorize(level)
            steps.append({"level": level.value, "allowed": decision.allowed, "reason": "; ".join(decision.reasons) or "Allowed in local demo", "providers": ", ".join(p.value for p in providers)})
        return tuple(steps)
