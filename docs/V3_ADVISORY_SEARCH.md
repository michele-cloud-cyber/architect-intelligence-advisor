# V3 AI advisory and module search

## Real local behavior

- deterministic scanners, Terraform parsing, CVE/CVSS demo dossier and FinOps ranges;
- normalized versioned state, secret redaction, input limits and fail-closed rules;
- central registry drives navigation, search terms, destination, badge and health;
- sidebar search and Ctrl+K/slash command palette perform navigation only;
- module failures remain isolated and fallback remains available.

## Simulated behavior

- Bedrock token and cost estimates;
- landing-zone storytelling, historical narrative and architecture suggestions;
- synthetic CVE/CVSS, multi-cloud inventory and FinOps values;
- current/proposed comparisons and remediation impact.

## Disabled/future behavior

No Bedrock client or cloud mutation path exists in V3. A future read-only advisory
connection requires explicit consent, temporary least-privilege role, model allowlist,
redaction, prompt-injection filtering, token/cost limits, timeout and local redacted
audit. It must never create findings, apply Terraform or mutate cloud resources.

## Keyboard behavior

- `Ctrl+K`: open command palette globally;
- `/`: open only outside editable fields;
- `↑` / `↓`: move selection;
- `Enter`: navigate to the selected module;
- `Esc`: close;
- browser `Ctrl+F`: unchanged.

Flows remain:

```text
Design → Simulation → Code → Test → CI/CD
Code → Architecture → Risk → FinOps → Remediation → Diff
```
