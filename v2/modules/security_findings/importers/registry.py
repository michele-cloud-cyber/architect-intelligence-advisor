"""Registry for independent Security Findings importer plugins."""

from __future__ import annotations

from v2.modules.security_findings.importers.base import SecurityFindingsImporter
from v2.modules.security_findings.importers.inspector import AmazonInspectorImporter
from v2.modules.security_findings.importers.nessus import NessusImporter
from v2.modules.security_findings.importers.nmap import NmapImporter
from v2.modules.security_findings.importers.openvas import OpenVasImporter
from v2.modules.security_findings.importers.security_hub import AwsSecurityHubImporter
from v2.modules.security_findings.models import SecuritySource


class ImporterRegistry:
    """Maps source identifiers to replaceable importer implementations."""

    def __init__(self, importers: tuple[SecurityFindingsImporter, ...] = ()) -> None:
        self._importers = {importer.source: importer for importer in importers}

    def register(self, importer: SecurityFindingsImporter) -> None:
        self._importers[importer.source] = importer

    def get(self, source: SecuritySource) -> SecurityFindingsImporter | None:
        return self._importers.get(source)

    def sources(self) -> tuple[SecuritySource, ...]:
        return tuple(sorted(self._importers, key=lambda source: source.value))


def default_importer_registry() -> ImporterRegistry:
    """Return only local, non-networking plugin declarations."""

    return ImporterRegistry(
        (
            NmapImporter(),
            NessusImporter(),
            OpenVasImporter(),
            AwsSecurityHubImporter(),
            AmazonInspectorImporter(),
        )
    )
