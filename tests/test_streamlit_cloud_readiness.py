"""Deployment guards for the demo-only Streamlit Community Cloud build."""

from pathlib import Path
import unittest

from streamlit.testing.v1 import AppTest


ROOT = Path(__file__).resolve().parents[1]


class StreamlitCloudReadinessTests(unittest.TestCase):
    def test_required_deployment_files_exist(self) -> None:
        for relative in ("streamlit_app.py", "requirements.txt", ".streamlit/config.toml"):
            self.assertTrue((ROOT / relative).is_file(), relative)

    def test_public_entrypoint_starts_without_exception(self) -> None:
        app = AppTest.from_file(ROOT / "streamlit_app.py")
        app.run(timeout=30)
        self.assertFalse(app.exception)
        self.assertIn(
            "AWS Interactive Architecture, Security & Terraform Lab",
            [item.value for item in app.title],
        )

    def test_public_build_disables_aws_and_bedrock_actions(self) -> None:
        source = (ROOT / "dashboard_v2/app.py").read_text(encoding="utf-8")
        self.assertIn("DEMO_ONLY = True", source)
        self.assertIn("demo_only=DEMO_ONLY", source)


if __name__ == "__main__":
    unittest.main()
