"""Regression guards for the module's local-only Phase 3 behavior."""

import unittest

from streamlit.testing.v1 import AppTest

from v2.modules.security_findings import service
from v2.modules.security_findings.importers import security_hub


class SecurityFindingsIsolationTests(unittest.TestCase):
    def test_module_does_not_construct_aws_or_bedrock_clients(self) -> None:
        self.assertNotIn("boto3", vars(service))
        self.assertNotIn("BedrockEngine", vars(service))
        self.assertNotIn("boto3", vars(security_hub))

    def test_existing_dashboard_process_has_no_runtime_exception(self) -> None:
        app = AppTest.from_file("app.py")
        app.run(timeout=30)

        self.assertFalse(app.exception)
