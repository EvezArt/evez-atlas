# Orchestrator Guide

This repository uses GitHub Issues and labels to trigger automation:

Labels:
- `task:build` — run build/test (Python pytest; optional Node tests)
- `task:test` — run Python tests
- `task:docs` — reserved for docs generation
- `task:cleanup` — reserved for formatting/cleanup tasks
- `task:deploy` — reserved for deploy tasks (requires `ok-to-run-destructive` label to be present)

Slash commands (issue comments):
- `/build` — triggers build/test
- `/test` — triggers tests

Branch protection:
- Enable on `main` to require CI and CodeQL checks before merging PRs.

Security notes:
- We do not use `pull_request_target` with checkout of PR head to avoid insecure patterns.
- Secret scanning runs with read‑only permissions and always uploads a JSON report artifact.

Trigger the loop:
1. Create an issue labeled `task:test` — the orchestrator will acknowledge and run tests.
2. Comment `/build` on any issue — the orchestrator will attempt build/test.

Fork safety:
- Workflows use least‑privilege permissions; no write actions to untrusted PR code.
