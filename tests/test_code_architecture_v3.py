"""V3 parser, malicious-input, FinOps, diff and intelligence tests."""

from io import BytesIO
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo
import unittest

from v2.modules.code_architecture import InputSecurityError, InputSecurityGateway, analyze_terraform, detect_changes, simulate_remediation


SAFE='''resource "aws_instance" "web" {
  ami = "ami-demo"
  instance_type = "t3.micro"
  metadata_options { http_endpoint = "enabled" http_put_response_hop_limit = 2 }
}
resource "aws_security_group" "web" {
  ingress { from_port = 22 to_port = 22 protocol = "tcp" cidr_blocks = ["0.0.0.0/0"] }
}
resource "aws_s3_bucket" "data" { bucket = "demo-data" }
'''


class InputSecurityGatewayTests(unittest.TestCase):
    def setUp(self): self.gateway=InputSecurityGateway()

    def test_safe_text_and_secret_redaction(self):
        secured=self.gateway.secure_text('resource "aws_instance" "x" { password = "secret-value" }')
        self.assertNotIn("secret-value",secured.files["main.tf"])
        self.assertEqual(secured.redacted_events,("secret-detected-and-redacted",))

    def test_blocks_local_remote_exec_files_network_and_remote_modules(self):
        malicious=(
            'resource "null_resource" "x" { provisioner "local-exec" { command="whoami" } }',
            'resource "null_resource" "x" { provisioner "remote-exec" {} }',
            'locals { x = file("../../secret") }', 'data "http" "x" { url="https://example" }',
            'module "x" { source="git::https://example/repo" }',
        )
        for text in malicious:
            with self.subTest(text=text), self.assertRaises(InputSecurityError):self.gateway.secure_text(text)

    def test_blocks_path_traversal_bad_extension_and_malformed_zip(self):
        for name in ("../main.tf","C:/main.tf","main.exe"):
            with self.subTest(name=name), self.assertRaises(InputSecurityError):self.gateway.secure_text("",name)
        with self.assertRaises(InputSecurityError):self.gateway.secure_zip(b"not-a-zip")

    def test_zip_bomb_ratio_and_symlink_are_blocked_safely(self):
        bomb=BytesIO()
        with ZipFile(bomb,"w",ZIP_DEFLATED) as archive: archive.writestr("main.tf","A"*200_000)
        with self.assertRaises(InputSecurityError):self.gateway.secure_zip(bomb.getvalue())
        symlink=BytesIO()
        with ZipFile(symlink,"w") as archive:
            info=ZipInfo("link.tf"); info.external_attr=(0o120777 << 16); archive.writestr(info,"main.tf")
        with self.assertRaises(InputSecurityError):self.gateway.secure_zip(symlink.getvalue())


class StaticArchitectureTests(unittest.TestCase):
    def test_parsing_graph_findings_imdsv2_and_finops(self):
        bundle=analyze_terraform({"main.tf":SAFE})
        self.assertEqual(len(bundle.resources),3)
        categories={f.category for f in bundle.findings}
        self.assertIn("Network",categories); self.assertIn("Compute Security",categories); self.assertIn("Encryption",categories)
        imds=next(f for f in bundle.findings if f.category=="Compute Security")
        self.assertIn('http_tokens = "required"',imds.remediation)
        self.assertIn("hop limit 2",imds.residual_risk)
        self.assertTrue(any(item.projected_annual is not None for item in bundle.finops))

    def test_simulation_preserves_original_and_generates_diff(self):
        bundle=analyze_terraform({"main.tf":SAFE}); selected=tuple(f.finding_id for f in bundle.findings if f.category in {"Network","Compute Security"})
        result=simulate_remediation(SAFE,bundle.findings,selected)
        self.assertEqual(result.original_code,SAFE)
        self.assertIn("10.0.0.0/8",result.proposed_code)
        self.assertIn('http_tokens = "required"',result.proposed_code)
        self.assertIn("proposed/main.tf",result.diff)
        self.assertLess(result.risk_after,result.risk_before)

    def test_intelligence_explains_new_risk_without_deciding(self):
        clean=analyze_terraform({"main.tf":SAFE.replace("0.0.0.0/0","10.0.0.0/8")})
        risky=analyze_terraform({"main.tf":SAFE})
        changes=detect_changes(clean,risky)
        self.assertTrue(any(item["change"]=="New risk" for item in changes))
        self.assertTrue(all("remediation" in item and "confidence" in item for item in changes))

    def test_malformed_terraform_is_reported_without_execution(self):
        bundle=analyze_terraform({"broken.tf":'resource "aws_s3_bucket" "x" {'})
        self.assertTrue(any("Malformed" in warning for warning in bundle.warnings))


if __name__=="__main__":unittest.main()
