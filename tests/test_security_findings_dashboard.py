"""Integration tests for the V2 Security Findings presentation boundary."""

import unittest

from streamlit.testing.v1 import AppTest

from sr.services.dashboard_service import DashboardService


class SecurityFindingsDashboardTests(unittest.TestCase):
    def test_dashboard_service_returns_demo_case_without_creating_history(self) -> None:
        service = DashboardService()
        dossier = service.get_demo_security_case()

        self.assertTrue(dossier.case_id.startswith("AIA-"))
        self.assertEqual(dossier.title, "Possible Internet-to-S3 compromise path through exposed EC2 workload")

    def test_dashboard_renders_security_findings_section(self) -> None:
        app = AppTest.from_file("app.py")
        app.run(timeout=30)

        self.assertFalse(app.exception)
        self.assertIn("Security Findings", [item.value for item in app.subheader])
