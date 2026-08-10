"""Integration tests for the V2 Security Findings presentation boundary."""

import unittest
from pathlib import Path

from streamlit.testing.v1 import AppTest

from sr.services.dashboard_service import DashboardService


APP_PATH = Path(__file__).resolve().parents[1] / "app.py"


class SecurityFindingsDashboardTests(unittest.TestCase):
    def test_dashboard_service_returns_demo_case_without_creating_history(self) -> None:
        service = DashboardService()
        dossier = service.get_demo_security_case()

        self.assertTrue(dossier.case_id.startswith("AIA-"))
        self.assertEqual(dossier.title, "Possible Internet-to-S3 compromise path through exposed EC2 workload")

    def test_dashboard_renders_security_findings_section(self) -> None:
        app = AppTest.from_file(APP_PATH)
        app.run(timeout=30)
        workspace = next(item for item in app.radio if item.label == "Workspace")
        workspace.set_value("Advisor Dashboard")
        app.run(timeout=30)

        self.assertFalse(app.exception)
        self.assertIn("Security Findings", [item.value for item in app.subheader])
