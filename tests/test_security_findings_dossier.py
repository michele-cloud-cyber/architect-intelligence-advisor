"""Tests for the deterministic, local-only demo investigative dossier."""

from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from v2.modules.security_findings.evidence_locker import evidence_fingerprint
from v2.modules.security_findings.repository import SecurityFindingsRepository
from v2.modules.security_findings.service import build_demo_security_case


class SecurityFindingsDossierTests(unittest.TestCase):
    def test_case_id_advances_without_collision(self) -> None:
        case = build_demo_security_case(("AIA-20260722-000001",))
        self.assertEqual(case.case_id, "AIA-20260722-000002")

    def test_correlation_is_deterministic_and_high_confidence(self) -> None:
        first = build_demo_security_case()
        second = build_demo_security_case()

        self.assertEqual(first.correlations, second.correlations)
        self.assertTrue(first.correlations)
        self.assertGreaterEqual(first.confidence_score, 70)
        self.assertTrue(all(item.label == "possible attack path" for item in first.correlations))

    def test_risk_score_exposes_components_and_formula(self) -> None:
        case = build_demo_security_case()

        self.assertIsNotNone(case.risk)
        assert case.risk is not None
        self.assertEqual(case.risk.score, 92)
        self.assertEqual(case.risk.level.value, "critical")
        self.assertTrue(case.risk.components)
        self.assertIn("additive", case.risk.formula)

    def test_timeline_is_chronological(self) -> None:
        case = build_demo_security_case()
        timestamps = [event.timestamp for event in case.timeline]

        self.assertEqual(timestamps, sorted(timestamps))
        self.assertEqual(case.timeline[0].event_type, "finding_detected")
        self.assertEqual(case.timeline[-1].event_type, "remediation_proposed")

    def test_evidence_fingerprint_is_deterministic_and_case_bound(self) -> None:
        case = build_demo_security_case()
        evidence = case.evidence[0]

        self.assertEqual(evidence.fingerprint, evidence_fingerprint(evidence))
        self.assertEqual(evidence.case_id, case.case_id)
        self.assertEqual(len(evidence.fingerprint), 64)

    def test_complete_dossier_serializes_and_loads(self) -> None:
        with TemporaryDirectory() as directory:
            repository = SecurityFindingsRepository(Path(directory))
            case = build_demo_security_case()
            repository.save_case(case)
            loaded = repository.get_case(case.case_id)

        self.assertEqual(loaded, case)
        self.assertIn("possible compromise chain", case.attack_story)
        self.assertTrue(case.attack_path)
        self.assertTrue(case.remediation)
