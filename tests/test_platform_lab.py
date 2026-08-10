"""Phase-one Platform Lab deterministic behavior tests."""

import unittest
from io import BytesIO
from zipfile import ZipFile

from v2.modules.platform_lab import OperatingMode, ProjectDefinition
from v2.modules.platform_lab.scoring import evaluate_controls, overall_score
from v2.modules.platform_lab.simulation import simulate_s3_changes
from v2.modules.platform_lab.terraform import generate_s3_package
from v2.modules.platform_lab.terraform import package_zip_bytes
from v2.modules.platform_lab.validation import validate_s3_package
from v2.modules.platform_lab.pipeline import github_actions_example


def project(configuration):
    return ProjectDefinition(
        "S3 Lab", "Protect artifacts", "Demo", ("S3",), ("sandbox",),
        ("development",), ("eu-west-1",), "app role", "Confidential", "TLS",
        "private encrypted storage", "audit", "regional", "versioning", "EUR 50",
        4, 1, "manual approval", OperatingMode.DEMO, configuration,
    )


class PlatformLabTests(unittest.TestCase):
    def setUp(self):
        self.current = {
            "block_public_access": False, "encryption": False, "versioning": False,
            "logging": False, "enforce_tls": False, "least_privilege": True,
            "monitoring": False, "lifecycle": False,
        }

    def test_scoring_is_weighted_and_deterministic(self):
        first = evaluate_controls(self.current)
        second = evaluate_controls(self.current)
        self.assertEqual(first, second)
        self.assertEqual(first[1]["IAM & Access Control"], 82)
        self.assertEqual(first[1]["Security"], 15)

    def test_simulation_attributes_every_score_change(self):
        changes = tuple(key for key, enabled in self.current.items() if not enabled)
        result = simulate_s3_changes(self.current, changes, project(self.current))
        self.assertGreater(result.after_overall, result.before_overall)
        self.assertLess(result.after_overall, 100)
        self.assertTrue(result.residual_risks)
        self.assertLess(result.confidence, 100)
        self.assertEqual(result.input_quality, 45)
        self.assertEqual(len(result.contributions), len(changes))
        self.assertFalse(result.new_risks)

    def test_secure_package_contains_required_s3_controls_and_no_credentials(self):
        changes = tuple(key for key, enabled in self.current.items() if not enabled)
        simulation = simulate_s3_changes(self.current, changes)
        package = generate_s3_package(project(self.current), simulation)
        main = package.files["main.tf"]
        self.assertIn("aws_s3_bucket_public_access_block", main)
        self.assertIn("aws_s3_bucket_server_side_encryption_configuration", main)
        self.assertIn("aws_s3_bucket_versioning", main)
        self.assertIn("aws_s3_bucket_logging", main)
        self.assertNotIn("aws_access_key", "".join(package.files.values()).lower())
        self.assertIn("tests/s3_security.tftest.hcl", package.files)

    def test_local_policy_checks_pass_and_real_plan_is_not_claimed(self):
        simulation = simulate_s3_changes(self.current, tuple(key for key, enabled in self.current.items() if not enabled))
        checks = validate_s3_package(generate_s3_package(project(self.current), simulation))
        custom = [item for item in checks if item.command.startswith("custom:")]
        self.assertTrue(custom)
        self.assertTrue(all(item.status == "Passed" for item in custom))
        plan = next(item for item in checks if item.check == "Terraform plan")
        self.assertEqual(plan.status, "Not executed")

    def test_italian_controls_translate_rationale_and_remediation(self):
        results, _ = evaluate_controls(self.current, "it")
        self.assertIn("non soddisfatto", results[0].rationale)
        self.assertIn("Abilita", results[0].definition.remediation)

    def test_terraform_download_contains_files_diff_and_traceability(self):
        simulation = simulate_s3_changes(self.current, tuple(key for key, enabled in self.current.items() if not enabled), project(self.current))
        package = generate_s3_package(project(self.current), simulation)
        self.assertIn("proposed/main.tf", package.diff)
        self.assertTrue(package.mappings)
        self.assertTrue(package.resource_explanations)
        with ZipFile(BytesIO(package_zip_bytes(package))) as archive:
            self.assertEqual(set(archive.namelist()), set(package.files))

    def test_pipeline_is_pinned_and_apply_is_inert_by_default(self):
        pipeline = github_actions_example()
        self.assertIn("actions/checkout@v4.2.2", pipeline)
        self.assertIn("actions/upload-artifact@v4.6.2", pipeline)
        self.assertIn("AWS_PLAN_ROLE_ARN", pipeline)
        self.assertIn("AWS_APPLY_ROLE_ARN", pipeline)
        self.assertIn("ENABLE_TERRAFORM_APPLY == 'true'", pipeline)
        self.assertIn("pull requests run quality checks only", pipeline.lower())


if __name__ == "__main__":
    unittest.main()
