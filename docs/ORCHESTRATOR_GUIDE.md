# GitHub Actions Orchestrator Guide

## Overview

The EvezArt/Evez666 repository uses an always-on automation loop powered by GitHub Actions workflows. This guide explains how to trigger tasks, understand the label vocabulary, and maintain safe, least-privilege operations.

## Core Workflows

### 1. Task Orchestrator (`orchestrator.yml`)
**Purpose:** Orchestrate tasks via issue labels and slash commands  
**Triggers:** Issue events (opened, labeled, reopened) and issue comments  
**Permissions:** `contents: read`, `issues: write` (minimal, fork-safe)

### 2. CI Pipeline (`ci.yml`)
**Purpose:** Continuous integration for Python and Node.js  
**Triggers:** Push to any branch, Pull requests  
**Permissions:** `contents: read` (read-only)

### 3. Secret Scanning (`gitleaks.yml`)
**Purpose:** Detect secrets and credentials in code  
**Triggers:** Pull requests, push to main, manual dispatch  
**Permissions:** `contents: read` (read-only)

### 4. Voice Artifact (`voice.yml`)
**Purpose:** Generate synthetic TTS message from "quantum future"  
**Triggers:** Push to main, manual dispatch  
**Permissions:** `contents: read` (read-only)

## Label Vocabulary

Use these labels on issues to trigger automated tasks:

| Label | Description | Action |
|-------|-------------|--------|
| `task:test` | Run Python tests | Executes pytest on the test suite |
| `task:build` | Build and test Node.js | Runs npm install and npm test |
| `task:docs` | Documentation task | Reserved for future doc generation |
| `task:cleanup` | Cleanup task | Reserved for cleanup operations |
| `task:deploy` | Deploy task | Reserved for deployment (requires `ok-to-run-destructive`) |

### Destructive Operations Gate

Some tasks could modify infrastructure or data. These require the `ok-to-run-destructive` label:
- This label is **not** added by default
- Only repository maintainers should add this label
- Used as a safety gate for deploy and cleanup operations

## Slash Commands

You can also trigger tasks via issue comments:

| Command | Action |
|---------|--------|
| `/test` | Run Python tests (pytest) |
| `/build` | Build and test Node.js |

**Example:**
```
/test
```

The orchestrator will acknowledge your command and execute the requested task.

## Fork Safety

All workflows follow GitHub Actions security best practices:

✅ **Safe Patterns:**
- Use `pull_request` trigger for PR validation (default GitHub token, no write access to PRs from forks)
- Use `contents: read` permission by default
- Only grant `issues: write` where needed (e.g., orchestrator comments)
- Checkout at default ref (not PR head) for untrusted PRs

❌ **Avoided Anti-Patterns:**
- **NO** `pull_request_target` with checkout of PR head (security risk)
- **NO** write tokens accessible to untrusted code
- **NO** secrets exposed to fork PRs

## Branch Protection

### Recommended Settings

Enable branch protection on `main` with these rules:

1. **Require status checks to pass:**
   - `python-ci` (from CI workflow)
   - `node-ci` (from CI workflow)
   - `CodeQL` (from PR #35)

2. **Require review from code owners:**
   - See `.github/CODEOWNERS` for required reviewers
   - Critical paths: workflows, requirements.txt, src/

3. **Require linear history:**
   - Prevents force pushes and ensures clean history

## Dependabot Integration

Weekly automated dependency updates via `.github/dependabot.yml`:
- **Python (pip):** Updates requirements.txt
- **npm:** Updates package.json and package-lock.json

Dependabot PRs will automatically trigger CI checks.

## How to Use

### Trigger a Test Run

**Option 1: Label**
1. Open or create an issue
2. Add the `task:test` label
3. Orchestrator runs tests and comments with results

**Option 2: Slash Command**
1. Comment `/test` on any issue
2. Orchestrator runs tests and comments with results

### Trigger a Build

**Option 1: Label**
1. Add the `task:build` label to an issue
2. Orchestrator installs dependencies and runs npm test

**Option 2: Slash Command**
1. Comment `/build` on any issue
2. Orchestrator builds and tests

### Run Secret Scan

1. Open a Pull Request (automatic)
2. Or: Go to Actions → Secret Scan → Run workflow

The scan report is always uploaded as an artifact, even if the scan passes.

### Generate Voice Artifact

1. Push to main (automatic)
2. Or: Go to Actions → Voice from the Future → Run workflow

Downloads `voice_future.mp3` artifact with synthetic message.

## Dry-Run Pattern

Workflows are designed with hooks for future dry-run modes:
- Commands check for destructive labels before proceeding
- Easy to add `DRY_RUN` environment variable checks later
- Provides safety for testing automation changes

## Creating Labels

After merging this PR, create the following labels in GitHub:

```bash
# Via GitHub CLI
gh label create "task:test" --description "Run Python tests" --color "0e8a16"
gh label create "task:build" --description "Build and test Node.js" --color "0e8a16"
gh label create "task:docs" --description "Documentation task" --color "1d76db"
gh label create "task:cleanup" --description "Cleanup task" --color "fbca04"
gh label create "task:deploy" --description "Deploy task" --color "d93f0b"
gh label create "ok-to-run-destructive" --description "Allow destructive operations" --color "d93f0b"
```

Or create them manually in the GitHub UI: Settings → Labels → New label

## Security Notes

- All workflows use least-privilege permissions
- No secrets are exposed to PRs from forks
- Gitleaks scans for leaked credentials on every PR
- CodeQL (from PR #35) provides additional code security scanning
- CODEOWNERS ensures critical changes are reviewed

## Troubleshooting

### Orchestrator doesn't respond
- Check that the label matches exactly (case-sensitive)
- Verify the workflow has `issues: write` permission
- Check Actions tab for workflow run status

### Tests fail in CI
- Review the CI logs in the Actions tab
- Check that requirements.txt and package.json are up to date
- Ensure tests pass locally before pushing

### Gitleaks reports issues
- Review the uploaded artifact for details
- Rotate any exposed credentials immediately
- Remove secrets from history if committed

## Future Enhancements

Planned additions:
- Deployment automation with `task:deploy` (gated by `ok-to-run-destructive`)
- Documentation generation with `task:docs`
- Automatic cleanup with `task:cleanup`
- Integration with external monitoring systems
- Advanced dry-run modes for testing

---

**Remember:** The orchestrator is fork-safe, least-privilege, and designed for autonomous operation. Let the automation work for you! 🤖✨
