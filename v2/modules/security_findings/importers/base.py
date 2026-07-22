"""Source plugin contract for future scanner ingestion."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TypeAlias

from v2.modules.security_findings.models import SecurityFinding, SecuritySource


ImportPayload: TypeAlias = bytes | str


class SecurityFindingsImporter(ABC):
    """Independent parser plugin with no dashboard or AWS dependency."""

    source: SecuritySource

    @abstractmethod
    def parse(self, payload: ImportPayload) -> tuple[SecurityFinding, ...]:
        """Normalize a source artifact into findings without persisting it."""


class DeferredImporter(SecurityFindingsImporter):
    """Plugin placeholder used until real source parsing is intentionally enabled."""

    def __init__(self, source: SecuritySource) -> None:
        self.source = source

    def parse(self, payload: ImportPayload) -> tuple[SecurityFinding, ...]:
        del payload
        raise NotImplementedError(
            f"{self.source.value} ingestion is prepared but not enabled in the demo-only MVP."
        )
