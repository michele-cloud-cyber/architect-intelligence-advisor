"""Non-published CI/CD examples for generated Terraform packages."""


def github_actions_example() -> str:
    return '''name: terraform-review
on: [pull_request]
permissions:
  contents: read
  id-token: write
jobs:
  checks:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: hashicorp/setup-terraform@v3
      - run: terraform fmt -check
      - run: terraform init -backend=false
      - run: terraform validate
      - run: terraform test
      - name: Security scan
        uses: bridgecrewio/checkov-action@v12
      - name: Plan with temporary OIDC credentials
        run: terraform plan -out=tfplan
        # Configure a least-privilege environment role before enabling this step.

# terraform apply intentionally omitted from pull requests.
# Production apply belongs in a separate protected workflow with manual approval.
'''
