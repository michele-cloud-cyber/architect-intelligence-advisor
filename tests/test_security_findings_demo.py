"""Tests for deterministic and complete Security Findings demo data."""

import unittest

from v2.modules.security_findings.demo import build_demo_findings


class DemoFindingsTests(unittest.TestCase):
    def test_demo_findings_contain_required_security_context(self) -> None:
        findings = build_demo_findings()

        self.assertGreaterEqual(len(findings), 3)
        for finding in findings:
            self.assertTrue(finding.finding_id)
            self.assertTrue(finding.asset_id)
            self.assertTrue(finding.hostname)
            self.assertTrue(finding.ip_address)
            self.assertGreaterEqual(finding.confidence, 0)
            self.assertLessEqual(finding.confidence, 1)
            self.assertTrue(finding.evidence)
