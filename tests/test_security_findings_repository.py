"""Unit tests for isolated Security Findings case persistence."""

from datetime import datetime
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from uuid import uuid4

from v2.modules.security_findings.models import CaseStatus, SecurityCase, SecuritySeverity
from v2.modules.security_findings.repository import SecurityFindingsRepository


class SecurityFindingsRepositoryTests(unittest.TestCase):
    def test_save_does_not_write_v1_history(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            repository = SecurityFindingsRepository(root)
            case = SecurityCase(
                case_id="AIA-20260722-000001",
                case_uuid=uuid4(),
                created_at=datetime(2026, 7, 22, 9, 0),
                status=CaseStatus.OPEN,
                severity=SecuritySeverity.HIGH,
                finding_ids=("demo-001",),
                asset_ids=("i-123",),
                correlated_vulnerabilities=("CVE-2026-0001",),
            )

            repository.save_case(case)

            self.assertTrue((root / "history" / "security_findings" / "cases" / f"{case.case_id}.json").exists())
            self.assertFalse(any((root / "history").glob("*.json")))
