"""Unit, contract and isolation tests for the multi-cloud foundation."""

import unittest

from v2.modules.multicloud_foundation import (
    AwsDemoAdapter, AzureDemoAdapter, GcpDemoAdapter, GovernanceControlPlane,
    LocalScenarioHistory, MultiCloudOrchestrator, OperationalLevel,
    PluginManifest, PluginRegistry, Provider, ScenarioSnapshot, adapter_registry,
)


class AdapterContractTests(unittest.TestCase):
    def test_all_demo_adapters_satisfy_common_contract(self):
        for adapter in (AwsDemoAdapter(), AzureDemoAdapter(), GcpDemoAdapter()):
            model = adapter.load_demo()
            self.assertFalse(adapter.live_connection)
            self.assertEqual(model.model_version, "1.0")
            self.assertTrue(model.metadata["synthetic"])
            self.assertTrue(model.resources)
            self.assertTrue(model.controls)
            self.assertEqual(adapter.validate(model), ())
            for control in model.controls:
                self.assertTrue(control.global_id)
                self.assertTrue(control.terraform_mapping)
                self.assertTrue(control.policy_mapping)
                self.assertTrue(control.test_mapping)
                self.assertTrue(control.rollback)

    def test_provider_isolation_rejects_foreign_model(self):
        errors = AwsDemoAdapter().validate(AzureDemoAdapter().load_demo())
        self.assertIn("Provider boundary violation", errors)


class GovernanceIsolationTests(unittest.TestCase):
    def test_dangerous_levels_are_fail_closed(self):
        governance = GovernanceControlPlane()
        for level in (OperationalLevel.PLAN, OperationalLevel.APPROVE, OperationalLevel.CONTROLLED_APPLY):
            self.assertFalse(governance.authorize(level).allowed)

    def test_sensitive_external_and_cross_environment_payloads_are_denied(self):
        governance = GovernanceControlPlane()
        for payload in ({"password": "value"}, {"publish": True}, {"network_access": True}, {"cross_environment": True}):
            self.assertFalse(governance.authorize(OperationalLevel.CONSULT, payload).allowed)
        self.assertNotIn("demo-value", governance.redact("password=demo-value"))

    def test_plugin_registry_enforces_allowlist_permissions_version_timeout_and_audit(self):
        manifest = PluginManifest("demo", "1.0.0", ("read",), ("metadata",), (), ("inventory:read",), (Provider.AWS,), {}, {}, 10, "fail-closed", True, "demo")
        registry = PluginRegistry(("demo",))
        registry.register(manifest)
        self.assertEqual(registry.manifests(), (manifest,))
        forbidden = PluginManifest("demo", "1.0.0", (), (), (), ("credentials",), (Provider.AWS,), {}, {}, 10, "fail-closed", True, "demo")
        with self.assertRaises(PermissionError): registry.register(forbidden)


class HistoryAndOrchestratorTests(unittest.TestCase):
    def test_history_is_immutable_and_comparable(self):
        model = AwsDemoAdapter().load_demo(); history = LocalScenarioHistory()
        first = ScenarioSnapshot("a", "current", "2026-01-01", "demo", "baseline", model, model, {"technical": 40}, ())
        second = ScenarioSnapshot("b", "desired", "2026-01-02", "demo", "improve", model, model, {"technical": 75}, ())
        history.append(first); history.append(second)
        self.assertEqual(history.compare("a", "b")["technical"]["delta"], 35)
        with self.assertRaises(ValueError): history.append(first)

    def test_orchestrator_uses_registered_adapters_and_governance(self):
        orchestrator = MultiCloudOrchestrator(adapter_registry(), GovernanceControlPlane(), LocalScenarioHistory(), PluginRegistry())
        models = orchestrator.overview((Provider.AWS, Provider.AZURE, Provider.GCP))
        self.assertEqual({m.resources[0].provider for m in models}, {Provider.AWS, Provider.AZURE, Provider.GCP})
        plan = orchestrator.execution_plan((Provider.AWS,))
        apply = next(step for step in plan if step["level"] == "controlled-apply")
        self.assertFalse(apply["allowed"])


if __name__ == "__main__":
    unittest.main()
