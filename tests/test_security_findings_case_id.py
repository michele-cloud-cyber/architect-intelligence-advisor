"""Unit tests for Security Findings Case ID allocation."""

from datetime import datetime
import unittest

from v2.modules.security_findings.case_id import allocate_case_id


class CaseIdTests(unittest.TestCase):
    def test_first_case_uses_sequence_one(self) -> None:
        case_id = allocate_case_id((), datetime(2026, 7, 22, 9, 0))
        self.assertEqual(case_id, "AIA-20260722-000001")

    def test_sequence_is_scoped_to_the_calendar_day(self) -> None:
        case_id = allocate_case_id(
            ("AIA-20260721-000099", "AIA-20260722-000004"),
            datetime(2026, 7, 22, 9, 0),
        )
        self.assertEqual(case_id, "AIA-20260722-000005")
