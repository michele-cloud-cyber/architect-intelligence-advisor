"""Tests for independent, non-networking importer plugin registration."""

import unittest

from v2.modules.security_findings.importers.registry import default_importer_registry
from v2.modules.security_findings.models import SecuritySource


class ImporterRegistryTests(unittest.TestCase):
    def test_default_registry_declares_requested_demo_mvp_sources(self) -> None:
        sources = set(default_importer_registry().sources())

        self.assertTrue(
            {
                SecuritySource.NMAP,
                SecuritySource.NESSUS,
                SecuritySource.OPENVAS,
                SecuritySource.AWS_SECURITY_HUB,
                SecuritySource.AMAZON_INSPECTOR,
            }.issubset(sources)
        )
