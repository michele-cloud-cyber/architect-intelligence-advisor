"""Amazon Inspector importer plugin declaration.

No boto3 client is created until a future real-ingestion phase.
"""

from v2.modules.security_findings.importers.base import DeferredImporter
from v2.modules.security_findings.models import SecuritySource


class AmazonInspectorImporter(DeferredImporter):
    def __init__(self) -> None:
        super().__init__(SecuritySource.AMAZON_INSPECTOR)
