# Troubleshooting Guide

This guide covers common issues and their solutions for the Evez666 repository.

## Table of Contents

- [Setup Issues](#setup-issues)
- [OpenClaw Integration](#openclaw-integration)
- [GitHub Actions](#github-actions)
- [API Integration](#api-integration)
- [Development Environment](#development-environment)

---

## Setup Issues

### Issue: Dependencies fail to install

**Symptoms:**
```
npm install fails with permission errors
```

**Solution:**
1. Ensure Node.js 20+ is installed: `node --version`
2. Clear npm cache: `npm cache clean --force`
3. Delete `node_modules` and `package-lock.json`, then reinstall:
   ```bash
   rm -rf node_modules package-lock.json
   npm install
   ```

### Issue: Python dependencies not found

**Symptoms:**
```
ModuleNotFoundError: No module named 'filterpy'
```

**Solution:**
1. Ensure Python 3.11+ is installed: `python --version`
2. Install requirements:
   ```bash
   pip install -r requirements.txt
   ```

---

## OpenClaw Integration

### Issue: OpenClaw skills not loading

**Symptoms:**
```
Skills directory not found or skills fail to load
```

**Solution:**
1. Verify skills directory exists:
   ```bash
   ls -la .openclaw/skills/
   ```
2. Check skill files are JavaScript modules with proper export syntax
3. Ensure SAFE_MODE is configured:
   ```bash
   export SAFE_MODE=true  # or false for active mode
   ```

### Issue: API keys not recognized

**Symptoms:**
```
[ChatGPT] OPENAI_API_KEY not found in environment
[Perplexity] PERPLEXITY_API_KEY not found in environment
```

**Solution:**
1. Set environment variables:
   ```bash
   export OPENAI_API_KEY="sk-..."
   export PERPLEXITY_API_KEY="pplx-..."
   export ANTHROPIC_API_KEY="sk-ant-..."
   export GITHUB_TOKEN="ghp_..."
   ```
2. In GitHub Codespaces:
   ```bash
   gh codespace set-secret OPENAI_API_KEY
   ```
3. Verify they're set:
   ```bash
   env | grep -E "(OPENAI|PERPLEXITY|ANTHROPIC|GITHUB_TOKEN)"
   ```

### Issue: Skills run in SAFE_MODE when I don't want them to

**Symptoms:**
```
[SAFE_MODE] API calls logged but not executed
```

**Solution:**
Set `SAFE_MODE=false` explicitly:
```bash
export SAFE_MODE=false
openclaw gateway start
```

**⚠️ Warning:** Disabling SAFE_MODE will allow actual API calls and GitHub operations. Ensure you understand the implications.

---

## GitHub Actions

### Issue: Workflow fails with permission denied

**Symptoms:**
```
Error: Resource not accessible by integration
```

**Solution:**
1. Check workflow has proper permissions in YAML:
   ```yaml
   permissions:
     contents: write
     pull-requests: write
   ```
2. Verify repository settings allow Actions to create PRs:
   - Settings → Actions → General → Workflow permissions
   - Select "Read and write permissions"

### Issue: Policy check fails on new workflow

**Symptoms:**
```
ERROR: workflow.yml uses pull_request_target (blocked by policy)
```

**Solution:**
1. Use `pull_request` instead of `pull_request_target`
2. Use `workflow_run` for dependent workflows
3. Add workflow to `.github/policy-allowlist.txt` if absolutely necessary (requires review)

### Issue: Secret scanning workflow fails

**Symptoms:**
```
TruffleHog failed or custom pattern check failed
```

**Solution:**
1. Remove any hardcoded secrets from code
2. Use `.env.example` for templates only
3. Never commit actual API keys
4. If secrets are in git history, use `git-filter-repo` to remove them

---

## API Integration

### Issue: OpenAI API calls fail

**Symptoms:**
```
Error: Invalid API key or rate limit exceeded
```

**Solution:**
1. Verify API key is valid and has sufficient credits
2. Check rate limits on your OpenAI account
3. Use lower rate models for testing:
   ```javascript
   const response = await agent.chatgpt.query(prompt, {
     model: 'gpt-3.5-turbo'  // Instead of gpt-4-turbo
   });
   ```

### Issue: GitHub API rate limit exceeded

**Symptoms:**
```
Error: API rate limit exceeded
```

**Solution:**
1. Use authenticated requests (GITHUB_TOKEN)
2. Implement caching for frequent requests
3. Reduce polling frequency
4. Check current rate limit:
   ```bash
   curl -H "Authorization: token $GITHUB_TOKEN" \
     https://api.github.com/rate_limit
   ```

### Issue: Perplexity API returns errors

**Symptoms:**
```
Error: API returned 401: Unauthorized
```

**Solution:**
1. Verify PERPLEXITY_API_KEY is set correctly
2. Ensure you have an active Perplexity subscription
3. Check model availability (some require Pro plan)
4. Use supported models:
   - `sonar-medium-online` (default)
   - `sonar-small-online`

---

## Development Environment

### Issue: TypeScript compilation fails

**Symptoms:**
```
error TS2307: Cannot find module 'X'
```

**Solution:**
1. Install TypeScript dependencies:
   ```bash
   npm install
   ```
2. Rebuild:
   ```bash
   npm run clean && npm run build
   ```
3. Check `tsconfig.json` is valid

### Issue: Tests fail

**Symptoms:**
```
Jest tests fail with module not found
```

**Solution:**
1. Ensure all dependencies are installed
2. Check test files use correct import syntax
3. Run specific test suite:
   ```bash
   npm test -- --testPathPattern=specific-test
   ```
4. Update snapshots if needed:
   ```bash
   npm test -- -u
   ```

### Issue: Codespaces won't start

**Symptoms:**
```
Codespace fails to build or times out
```

**Solution:**
1. Check `.devcontainer/devcontainer.json` syntax
2. Verify postCreateCommand doesn't hang
3. Try rebuilding the container:
   - Command Palette → "Codespaces: Rebuild Container"
4. Check Codespaces logs for specific errors

---

## Metrics Dashboard

### Issue: Metrics dashboard not updating

**Symptoms:**
```
docs/METRICS.md not updated or shows stale data
```

**Solution:**
1. Check metrics-dashboard workflow runs:
   ```bash
   gh workflow view metrics-dashboard
   ```
2. Manually trigger workflow:
   ```bash
   gh workflow run metrics-dashboard.yml
   ```
3. Verify permissions for workflow to commit:
   ```yaml
   permissions:
     contents: write
   ```

---

## Health Checks

### Issue: Health check fails

**Symptoms:**
```
Service reported as unhealthy
```

**Solution:**
1. Run health check manually:
   ```bash
   node scripts/health-check.js
   ```
2. Check individual service status
3. Review logs for errors
4. Ensure all required environment variables are set

---

## Getting Help

If you encounter an issue not covered here:

1. **Check existing issues:** Search [GitHub Issues](https://github.com/EvezArt/Evez666/issues)
2. **Review documentation:** See `docs/` directory for detailed guides
3. **Check logs:** Review workflow logs in Actions tab
4. **Create an issue:** Open a new issue with:
   - Clear description of the problem
   - Steps to reproduce
   - Error messages
   - Environment details (OS, Node version, etc.)

---

## Quick Reference

### Essential Commands

```bash
# Install dependencies
npm install
pip install -r requirements.txt

# Build
npm run build

# Test
npm test
pytest src/tests/python/ -v

# Lint
npm run lint

# Run OpenClaw
openclaw gateway start

# Check health
node scripts/health-check.js
```

### Environment Variables

```bash
# Required for OpenClaw skills
export OPENAI_API_KEY="sk-..."
export PERPLEXITY_API_KEY="pplx-..."
export ANTHROPIC_API_KEY="sk-ant-..."
export GITHUB_TOKEN="ghp_..."

# Optional configuration
export SAFE_MODE=true              # Enable safe mode (default)
export DEBUG=true                  # Enable debug logging
export INTROSPECTION_INTERVAL=60000  # Self-awareness interval (ms)
export DEEPCLAW_INTERVAL=300000    # DeepClaw analysis interval (ms)
export ORCHESTRATOR_INTERVAL=600000  # Orchestrator check interval (ms)
```

### File Locations

- **Workflows:** `.github/workflows/`
- **Skills:** `.openclaw/skills/`
- **Docs:** `docs/`
- **Tests:** `src/tests/`, `tests/`
- **Metrics:** `data/metrics/`
- **Logs:** Check workflow logs in GitHub Actions

---

*Last updated: 2026-02-14*
