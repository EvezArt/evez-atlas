# Orchestrator Guide

Labels:
- `task:build` — run build/test (Python pytest; optional Node tests)
- `task:test` — run Python tests
- `task:docs` — reserved for docs generation
- `task:cleanup` — reserved for formatting/cleanup tasks
- `task:deploy` — reserved for deploy tasks (requires `ok-to-run-destructive` label to be present)

Slash commands:
- `/build` — triggers build/test
- `/test` — triggers tests

Branch protection:
- Enable on `main` to require CI and CodeQL checks before merging PRs.

Security notes:
- No `pull_request_target` with checkout of PR head.
- Secret scanning: read-only permissions; always uploads JSON report.

Trigger the loop:
1. Create an issue labeled `task:test` — the orchestrator will acknowledge and run tests.
2. Comment `/build` on any issue — the orchestrator will attempt build/test.
