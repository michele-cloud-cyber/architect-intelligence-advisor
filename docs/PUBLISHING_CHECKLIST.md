# GitHub and LinkedIn publication checklist

## Before GitHub

- [ ] Confirm the license choice; do not replace `LICENSE` without approval.
- [ ] Review commit history and repository visibility.
- [ ] Re-run the full test suite from a clean environment.
- [ ] Verify ZIP SHA-256 and scan for credentials, `.env`, state and caches.
- [ ] Confirm screenshots contain synthetic names only.
- [ ] Confirm no AWS/Azure/GCP account IDs, tenant IDs or project IDs are present.
- [ ] Add repository topics: `cloud-architecture`, `terraform`, `security`, `finops`, `streamlit`.
- [ ] Enable branch protection and secret scanning if the repository is published.

## LinkedIn portfolio post

- [ ] Lead with the problem: fragmented architecture, security and cost decisions.
- [ ] Show both flows: requirements→code and code→architecture.
- [ ] Include one overview, one architecture-risk and one before/after screenshot.
- [ ] State clearly: local demo, synthetic data, no credentials, no cloud mutations.
- [ ] Mention tested fallback and malicious-input protections.
- [ ] Link to the repository only after the GitHub checklist is complete.
- [ ] Avoid implying real cloud compliance or production price accuracy.

Nothing in this checklist performs publication automatically.
