"""Fallback, health, isolation and launcher tests for the unified shell."""

from pathlib import Path
import unittest

from v2.modules.unified_shell import HealthStatus, NormalizedAppState, probe_modules


ROOT = Path(__file__).resolve().parents[1]


class UnifiedStateTests(unittest.TestCase):
    def test_state_is_versioned_immutable_and_normalized(self):
        state = NormalizedAppState()
        changed = state.evolve(active_view="Versione stabile", operating_mode="Simulation")
        self.assertEqual(state.active_view, "Vista completa")
        self.assertEqual(changed.schema_version, "1.0")
        self.assertEqual(changed.active_view, "Versione stabile")
        with self.assertRaises(ValueError): state.evolve(operating_mode="Live")

    def test_forced_module_failure_is_isolated(self):
        health = {item.module_id: item for item in probe_modules("multicloud")}
        self.assertEqual(health["multicloud"].status, HealthStatus.UNAVAILABLE)
        self.assertEqual(health["stable_lab"].status, HealthStatus.AVAILABLE)

    def test_finops_interface_is_available_and_isolated(self):
        health = {item.module_id: item for item in probe_modules()}
        self.assertEqual(health["finops"].status, HealthStatus.AVAILABLE)
        self.assertEqual(health["stable_lab"].status, HealthStatus.AVAILABLE)


class LauncherContractTests(unittest.TestCase):
    def test_three_entry_points_remain_separate(self):
        self.assertTrue((ROOT / "streamlit_app.py").is_file())
        self.assertTrue((ROOT / "demo_streamlit_app.py").is_file())
        self.assertTrue((ROOT / "unified_app.py").is_file())
        self.assertIn("dashboard_v2", (ROOT / "streamlit_app.py").read_text(encoding="utf-8"))
        self.assertIn("multicloud_foundation", (ROOT / "demo_streamlit_app.py").read_text(encoding="utf-8"))
        self.assertIn("render_unified_application", (ROOT / "unified_app.py").read_text(encoding="utf-8"))

    def test_launchers_target_their_own_entry_points(self):
        stable = (ROOT / "start_app.bat").read_text(encoding="utf-8")
        foundation = (ROOT / "start_foundation_app.bat").read_text(encoding="utf-8")
        complete = (ROOT / "start_complete_app.bat").read_text(encoding="utf-8")
        self.assertIn("streamlit_app.py", stable)
        self.assertIn("demo_streamlit_app.py", foundation)
        self.assertIn("unified_app.py", complete)


if __name__ == "__main__":
    unittest.main()
