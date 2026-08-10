"""Phase-one Platform Lab deterministic behavior tests."""

import unittest

from v2.modules.platform_lab import OperatingMode, ProjectDefinition
from v2.modules.platform_lab.scoring import evaluate_controls, overall_score
from v2.modules.platform_lab.simulation import simulate_s3_changes
from v2.modules.platform_lab.terraform import generate_s3_package
from v2.modules.platform_lab.validation import validate_s3_package


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
        self.assertEqual(first[1]["IAM & Access Control"], 100)
        self.assertEqual(first[1]["Security"], 0)

    def test_simulation_attributes_every_score_change(self):
        changes = tuple(key for key, enabled in self.current.items() if not enabled)
        result = simulate_s3_changes(self.current, changes)
        self.assertGreater(result.after_overall, result.before_overall)
        self.assertEqual(result.after_overall, 100)
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


if __name__ == "__main__":
    unittest.main()
