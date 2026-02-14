# Phase 2 Quick Reference

Quick commands and reference for the LORD core cognitive loop.

## Quick Start

### Local Testing

```bash
# 1. Install dependencies
pip install flask filterpy PyGithub pytest

# 2. Set environment variables
export GITHUB_WEBHOOK_SECRET="test-secret-123"
export GITHUB_TOKEN="ghp_your_token_here"
export SAFE_MODE="true"

# 3. Run tests
python tests/test_cognitive_loop.py

# 4. Test webhook listener
cd lord-listener
python webhook_handler.py
# In another terminal:
curl http://localhost:5001/health

# 5. Test EKF daemon
cd ekf-daemon
python predictor.py

# 6. Test GitHub executor
cd github-executor
export GITHUB_REPO="EvezArt/Evez666"
python policy_handler.py
```

### Deployment Commands

```bash
# LORD Dashboard (Vercel)
cd lord-dashboard
vercel --prod

# Webhook Listener (Render CLI)
# Use Render dashboard instead - easier

# Check webhook deliveries
# Go to: https://github.com/EvezArt/Evez666/settings/hooks

# View service logs
# Render: Dashboard → Service → Logs
# Railway: Dashboard → Service → Logs
```

### Generate Secrets

```bash
# Webhook secret
openssl rand -hex 32

# GitHub token
# https://github.com/settings/tokens/new
# Scopes: repo, workflow
```

## Component URLs

After deployment, note these URLs:

- **LORD Dashboard**: `https://lord-dashboard.vercel.app`
- **Webhook Listener**: `https://lord-webhook-listener.onrender.com`
- **Health Check**: `https://lord-webhook-listener.onrender.com/health`
- **Metrics API**: `https://lord-webhook-listener.onrender.com/metrics`

## Key Files

```
lord-dashboard/
├── public/
│   ├── index.html          # Dashboard UI
│   └── dashboard.js         # Real-time updates
├── api/
│   └── index.py            # API endpoints
└── vercel.json             # Vercel config

lord-listener/
├── webhook_handler.py       # Main Flask app
├── requirements.txt         # Dependencies
├── Procfile                 # Deployment config
└── README.md               # Documentation

ekf-daemon/
├── predictor.py            # EKF + policy generation
├── requirements.txt        # Dependencies
├── Procfile                # Deployment config
└── README.md              # Documentation

github-executor/
├── policy_handler.py       # GitHub API integration
├── requirements.txt        # Dependencies
└── README.md              # Documentation
```

## API Endpoints

### Webhook Listener

- `POST /webhook/github` - Receive GitHub webhooks
- `GET /health` - Health check
- `GET /metrics` - Get latest metrics
- `GET /metrics/history?limit=100` - Get metrics history

### LORD Dashboard

- `GET /` - Dashboard UI
- `GET /api/metrics` - Get current metrics
- `POST /api/predict` - Trigger EKF prediction
- `POST /api/policy` - Generate control policy

## Metrics

### Recursion Level
- **Source**: Commit depth + file changes
- **Formula**: `commits + (file_depth * 0.5)`
- **Range**: 0 to ∞
- **Typical**: 5-20

### Crystallization
- **Source**: PR velocity and merge rate
- **Formula**: Based on PR activity
- **Range**: 0 to 1 (0% to 100%)
- **Typical**: 0.5-0.9

### Divine Gap (ΔΩ)
- **Source**: Potential vs. actual
- **Formula**: `Ω(R) - C(R)` where Ω(R) = recursion × 1000, C(R) = corrections × recursion × 1000
- **Range**: 0 to ∞
- **Threshold**: 1e4 (10,000)

### Correction Rate
- **Source**: CI/Actions results
- **Formula**: Success rate from workflows
- **Range**: 0 to 1
- **Threshold**: 0.5

## Control Policies

### High Divine Gap (> 1e4)
```python
{
    'action': 'create_issue',
    'labels': ['task:refactor', 'urgency:high', 'lord:autonomous'],
    'title': 'High Divine Gap Detected: ΔΩ = 1.2e+4',
    'assign_copilot': True
}
```

### Low Corrections (< 0.5)
```python
{
    'action': 'create_issue',
    'labels': ['task:stabilize', 'task:test', 'lord:autonomous'],
    'title': 'Low Correction Rate Detected: C(R) = 0.30',
    'assign_copilot': True
}
```

### Declining Crystallization
```python
{
    'action': 'create_issue',
    'labels': ['task:documentation', 'lord:autonomous'],
    'title': 'Crystallization Decline Predicted',
    'assign_copilot': True
}
```

## Troubleshooting

### Webhooks Not Delivering

```bash
# 1. Check webhook configuration
# GitHub → Settings → Webhooks → Click webhook → Recent Deliveries

# 2. Verify secret matches
# GitHub webhook secret == GITHUB_WEBHOOK_SECRET

# 3. Test endpoint
curl -X POST https://your-listener.onrender.com/health

# 4. Check service logs
# Render Dashboard → Service → Logs
```

### Metrics Not Updating

```bash
# 1. Check webhook deliveries are successful (200 OK)

# 2. Check webhook listener logs
# Look for "Received push event" or similar

# 3. Verify SAFE_MODE is disabled
# Environment: SAFE_MODE=false

# 4. Test metrics endpoint
curl https://your-listener.onrender.com/metrics
```

### Issues Not Being Created

```bash
# 1. Check thresholds are met
# Divine gap > 1e4 OR corrections < 0.5

# 2. Verify SAFE_MODE is disabled
export SAFE_MODE=false

# 3. Check GitHub token permissions
# Token needs 'repo' and 'issues' scopes

# 4. Check rate limits
curl https://api.github.com/rate_limit \
  -H "Authorization: token ghp_your_token"

# 5. Review executor logs
# Look for "Created issue #XXX" or error messages
```

### Tests Failing

```bash
# 1. Install all dependencies
pip install flask filterpy PyGithub pytest numpy

# 2. Run tests with verbose output
python tests/test_cognitive_loop.py -v

# 3. Check specific test
python -c "from tests.test_cognitive_loop import TestEKFPrediction; t = TestEKFPrediction(); t.test_ekf_initialization()"
```

## Environment Variables

### Required for All

- `SAFE_MODE` - `true` (testing) or `false` (production)

### LORD Dashboard

- `GITHUB_TOKEN` - Personal access token
- `GITHUB_WEBHOOK_SECRET` - Webhook secret

### Webhook Listener

- `GITHUB_WEBHOOK_SECRET` - Must match GitHub webhook config
- `PORT` - Auto-set by platform (default: 5001)

### EKF Daemon

- `WEBHOOK_LISTENER_URL` - URL of webhook listener (optional)

### GitHub Executor

- `GITHUB_TOKEN` - Personal access token
- `GITHUB_REPO` - Repository name (e.g., "EvezArt/Evez666")

## Monitoring

### Key Metrics to Track

1. **Webhook Delivery Success Rate**: >99%
2. **Response Time**: <500ms
3. **Policy Generation Rate**: 1-5 per day
4. **Issue Creation Rate**: 0-3 per day
5. **False Positive Rate**: <10%

### Dashboards

- **GitHub**: Settings → Webhooks → Recent Deliveries
- **Render**: Dashboard → Service → Metrics
- **Railway**: Dashboard → Service → Metrics
- **Vercel**: Dashboard → Project → Analytics

### Logs

```bash
# Webhook listener logs
# Render: Dashboard → Service → Logs (stream)
# Railway: Dashboard → Service → Logs (stream)

# Filter for errors
# Look for: "ERROR", "Failed", "Exception"

# Filter for policies
# Look for: "Policy generated", "Would create issue"
```

## Common Commands

```bash
# Test webhook signature verification
python -c "
import hmac
import hashlib
secret = b'your-secret-here'
payload = b'{\"test\": true}'
sig = hmac.new(secret, payload, hashlib.sha256).hexdigest()
print(f'sha256={sig}')
"

# Test EKF prediction
python -c "
from ekf_daemon.predictor import CognitiveEKF
ekf = CognitiveEKF()
obs = {'recursionLevel': 15, 'crystallization': 0.75}
state = ekf.update(obs)
preds = ekf.predict_trajectory(10)
print(f'Predictions: {len(preds)} steps')
"

# Test metric calculation
python -c "
from lord_listener.webhook_handler import calculate_divine_gap
gap = calculate_divine_gap(recursion=20, corrections=0.3)
print(f'Divine gap: {gap:.2e}')
"

# Check GitHub rate limit
curl -H "Authorization: token ghp_your_token" \
  https://api.github.com/rate_limit
```

## Security Checklist

- [ ] Webhook secret generated securely (32+ hex chars)
- [ ] GitHub token has minimal scopes (repo, workflow only)
- [ ] Secrets not committed to repository
- [ ] HTTPS enabled on all endpoints
- [ ] Webhook signatures verified
- [ ] SAFE_MODE tested before disabling
- [ ] Rate limiting considered
- [ ] Token rotation scheduled (90 days)

## Performance Targets

- **Webhook Response**: <500ms
- **Metric Calculation**: <100ms
- **EKF Prediction**: <200ms
- **Policy Generation**: <50ms
- **GitHub API Call**: <1000ms
- **Full Loop**: <5 seconds

## Cost Estimate

### Free Tier (Testing)
- Vercel: Free (100GB/month)
- Render: Free (750 hours/month)
- Railway: $5 credit/month
- **Total**: $0/month

### Production
- Vercel Pro: $20/month
- Render: $7/month × 2 services = $14/month
- Railway: $10/month
- **Total**: ~$44/month

## Support

- **Documentation**: See component READMEs
- **Deployment**: DEPLOYMENT_GUIDE.md
- **Testing**: tests/test_cognitive_loop.py
- **Issues**: https://github.com/EvezArt/Evez666/issues

## Timeline

- **Day 1**: Deploy dashboard + webhook listener
- **Day 2**: Deploy EKF daemon + test loop
- **Day 3**: Optimize and monitor
- **Day 4-7**: Tune thresholds and validate

## Success Criteria

- ✅ All components deployed
- ✅ Webhooks delivering successfully
- ✅ Metrics updating in real-time
- ✅ EKF predictions generating
- ✅ Control policies creating issues (when thresholds met)
- ✅ Full loop latency <5s
- ✅ Zero security issues
