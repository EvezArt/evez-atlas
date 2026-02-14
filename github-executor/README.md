# GitHub Policy Executor

Executes control policies by creating GitHub resources (issues, PRs, comments).

## Overview

The GitHub executor is the final step in the LORD cognitive loop, converting control policies into concrete GitHub actions.

```
EKF Daemon → Control Policy → GitHub Executor → GitHub API → Issues/PRs
```

## Features

- **Create Issues**: Generate issues from control policies
- **Create PRs**: Create pull requests for code changes
- **Add Comments**: Comment on existing issues/PRs
- **Assign Copilot**: Automatically assign Copilot to issues
- **Duplicate Detection**: Prevent duplicate issues
- **SAFE_MODE**: Log actions instead of executing

## Configuration

### Environment Variables

- `GITHUB_TOKEN` (required): GitHub personal access token
- `GITHUB_REPO` (default: EvezArt/Evez666): Target repository
- `SAFE_MODE` (default: true): When enabled, logs instead of executing

### GitHub Token Permissions

Required scopes:
- `repo` - Full repository access
- `issues` - Create and modify issues
- `pull_requests` - Create and modify PRs
- `workflows` - Trigger workflows (optional)

Generate token at: https://github.com/settings/tokens/new

## Usage

### As Python Module

```python
from policy_handler import PolicyExecutor

executor = PolicyExecutor(
    github_token="ghp_...",
    repo_name="EvezArt/Evez666"
)

policy = {
    'action': 'create_issue',
    'labels': ['task:refactor', 'urgency:high'],
    'title': 'High Divine Gap Detected',
    'body': 'Metrics indicate refactoring needed...',
    'assign_copilot': True,
    'reason': 'divine_gap_threshold'
}

result = executor.execute_policy(policy)
```

### As Serverless Function

Deploy as AWS Lambda, Google Cloud Function, or Vercel Function:

```python
# handler.py
from policy_handler import PolicyExecutor
import json

def handler(event, context):
    policy = json.loads(event['body'])
    
    executor = PolicyExecutor()
    result = executor.execute_policy(policy)
    
    return {
        'statusCode': 200,
        'body': json.dumps({'result': str(result)})
    }
```

### As Standalone Service

```bash
# Run once
python policy_handler.py

# Run as HTTP service (with Flask)
# See lord-listener/webhook_handler.py for example
```

## Policy Structure

### Create Issue

```python
{
    'action': 'create_issue',
    'title': 'Issue Title',
    'body': 'Issue description with metrics...',
    'labels': ['task:refactor', 'urgency:high', 'lord:autonomous'],
    'assign_copilot': True,
    'reason': 'divine_gap_threshold'
}
```

### Create Pull Request

```python
{
    'action': 'create_pr',
    'title': 'PR Title',
    'body': 'PR description...',
    'head': 'feature-branch',
    'base': 'main',
    'labels': ['lord:autonomous']
}
```

### Add Comment

```python
{
    'action': 'add_comment',
    'issue_number': 123,
    'comment': 'Additional context...'
}
```

## SAFE_MODE

### When Enabled (default)

- Actions are logged but not executed
- Full policy details printed to console
- Returns dict with `safe_mode: True`
- Safe for testing and development

```python
# Output:
SAFE_MODE: Would create issue:
Title: High Divine Gap Detected
Labels: ['task:refactor', 'urgency:high']
Body: ...
```

### When Disabled

- Actions are executed against GitHub
- Issues and PRs are actually created
- Requires valid GITHUB_TOKEN
- Should only be enabled after testing

```bash
export SAFE_MODE=false
python policy_handler.py
```

## Duplicate Detection

Before creating issues, check for duplicates:

```python
if not executor.check_duplicate_issue('High Divine Gap', days=7):
    executor.execute_policy(policy)
else:
    print("Duplicate issue exists, skipping")
```

## Copilot Assignment

Automatically assign Copilot to issues:

```python
# 1. Add 'copilot:requested' label
# 2. Add comment mentioning @copilot

executor.assign_copilot_to_issue(issue_number=123)
```

## Integration

### With EKF Daemon

```python
# In EKF daemon
from github_executor.policy_handler import PolicyExecutor

executor = PolicyExecutor()

policy = ekf.generate_control_policy(state, predictions, corrections)
if policy:
    executor.execute_policy(policy)
```

### With Webhook Listener

```python
# In webhook handler
@app.route('/execute-policy', methods=['POST'])
def execute_policy_endpoint():
    policy = request.json
    executor = PolicyExecutor()
    result = executor.execute_policy(policy)
    return jsonify({'result': str(result)})
```

## Deployment

### AWS Lambda

1. Package with dependencies:
```bash
pip install -t package/ -r requirements.txt
cp policy_handler.py package/
cd package && zip -r ../function.zip .
```

2. Upload to Lambda
3. Set environment variables
4. Configure trigger (API Gateway, EventBridge)

### Google Cloud Functions

```bash
gcloud functions deploy execute-policy \
  --runtime python311 \
  --trigger-http \
  --entry-point handler \
  --set-env-vars GITHUB_TOKEN=$TOKEN,SAFE_MODE=false
```

### Vercel Functions

```python
# api/execute.py
from github_executor.policy_handler import PolicyExecutor
from flask import request, jsonify

def handler(request):
    policy = request.json
    executor = PolicyExecutor()
    result = executor.execute_policy(policy)
    return jsonify({'result': str(result)})
```

## Error Handling

The executor catches GitHub API exceptions:

```python
try:
    result = executor.execute_policy(policy)
except GithubException as e:
    print(f"GitHub API error: {e}")
except ValueError as e:
    print(f"Configuration error: {e}")
```

## Rate Limiting

GitHub API has rate limits:
- Authenticated: 5,000 requests/hour
- Per-resource: Varies by endpoint

Monitor rate limits:

```python
rate = executor.gh.get_rate_limit()
print(f"Core: {rate.core.remaining}/{rate.core.limit}")
print(f"Search: {rate.search.remaining}/{rate.search.limit}")
```

## Security

### Token Storage

- Never commit tokens to repository
- Use environment variables or secrets manager
- Rotate tokens regularly
- Use minimal required permissions

### SAFE_MODE in Production

- Start with SAFE_MODE=true
- Review generated policies
- Gradually enable for low-risk actions
- Monitor for unexpected behavior

### Issue Content

- Sanitize policy data before adding to issues
- Don't include sensitive information
- Add clear attribution (LORD generated)
- Include timestamp and metadata

## Testing

### Unit Tests

```bash
cd github-executor
pytest test_policy_handler.py
```

### Integration Tests

```python
# Test with real GitHub API
import os
os.environ['GITHUB_TOKEN'] = 'ghp_test...'
os.environ['SAFE_MODE'] = 'true'

from policy_handler import PolicyExecutor

executor = PolicyExecutor()
policy = {'action': 'create_issue', ...}
result = executor.execute_policy(policy)
assert result['safe_mode'] == True
```

## Monitoring

Track these metrics:
- Policy execution success rate
- API rate limit usage
- Issue creation rate
- Duplicate detection rate
- Copilot assignment success rate

## Troubleshooting

### Authentication Failed

```
Check:
- Token is valid
- Token has required scopes
- Token not expired
- Environment variable set correctly
```

### Rate Limit Exceeded

```
Wait for rate limit reset
Use conditional requests (ETag)
Implement exponential backoff
Consider GitHub Apps for higher limits
```

### Duplicate Issues

```
Enable duplicate detection
Increase check window (days)
Use more specific title prefixes
```

## Future Enhancements

- [ ] Batch policy execution
- [ ] Priority queue for policies
- [ ] Retry logic with exponential backoff
- [ ] Webhook notifications for policy execution
- [ ] Analytics dashboard
- [ ] Multi-repository support
- [ ] Custom label management
- [ ] Automated PR content generation
