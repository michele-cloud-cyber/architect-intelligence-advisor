"""Non-published, apply-disabled CI/CD example for generated Terraform."""


def github_actions_example() -> str:
    return '''name: terraform-controlled-delivery
on:
  pull_request:
  workflow_dispatch:
    inputs:
      environment:
        type: choice
        options: [development, staging, production]
      enable_apply:
        type: boolean
        default: false

permissions:
  contents: read
  id-token: write

jobs:
  quality:
    runs-on: ubuntu-24.04
    steps:
      - uses: actions/checkout@v4.2.2
      - uses: hashicorp/setup-terraform@v3.1.2
        with: { terraform_version: 1.10.5 }
      - run: terraform fmt -check -recursive
      - run: terraform init -backend=false
      - run: terraform validate
      - run: terraform test
      - uses: bridgecrewio/checkov-action@v12.3058.0
        with: { directory: ., framework: terraform }
      - name: Policy as Code
        run: ./scripts/policy-check.sh

  plan:
    needs: quality
    if: github.event_name == 'workflow_dispatch'
    environment: ${{ inputs.environment }}-plan
    permissions: { contents: read, id-token: write }
    steps:
      - uses: actions/checkout@v4.2.2
      - uses: aws-actions/configure-aws-credentials@v4.1.0
        with:
          role-to-assume: ${{ vars.AWS_PLAN_ROLE_ARN }}
          aws-region: ${{ vars.AWS_REGION }}
      - uses: hashicorp/setup-terraform@v3.1.2
      - run: terraform init
      - run: terraform plan -out=tfplan
      - uses: actions/upload-artifact@v4.6.2
        with: { name: terraform-plan-${{ inputs.environment }}, path: tfplan }

  apply:
    needs: plan
    if: github.event_name == 'workflow_dispatch' && inputs.enable_apply == true && vars.ENABLE_TERRAFORM_APPLY == 'true'
    environment: ${{ inputs.environment }}-apply # configure required reviewers
    permissions: { contents: read, id-token: write }
    steps:
      - uses: actions/checkout@v4.2.2
      - uses: aws-actions/configure-aws-credentials@v4.1.0
        with:
          role-to-assume: ${{ vars.AWS_APPLY_ROLE_ARN }}
          aws-region: ${{ vars.AWS_REGION }}
      - uses: actions/download-artifact@v4.1.8
        with: { name: terraform-plan-${{ inputs.environment }} }
      - uses: hashicorp/setup-terraform@v3.1.2
      - run: terraform apply tfplan

# Pull requests run quality checks only: they cannot plan or apply.
# Apply is inert until ENABLE_TERRAFORM_APPLY=true, a distinct least-privilege
# OIDC apply role exists, and the protected environment grants manual approval.
'''
