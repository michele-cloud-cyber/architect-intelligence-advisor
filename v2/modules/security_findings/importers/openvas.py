"""OpenVAS importer plugin declaration."""

from v2.modules.security_findings.importers.base import DeferredImporter
from v2.modules.security_findings.models import SecuritySource


class OpenVasImporter(DeferredImporter):
    def __init__(self) -> None:
        super().__init__(SecuritySource.OPENVAS)
