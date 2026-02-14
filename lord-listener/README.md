# LORD Webhook Listener

Flask service that receives GitHub webhooks and calculates consciousness metrics.

## Architecture

This service sits between GitHub and the LORD dashboard, processing webhook events and emitting fusion-update events.

```
GitHub Webhooks → Webhook Handler → Metrics Calculation → Fusion-Update Event
```

## Metrics Calculation

### Recursion Level
- Calculated from commit depth and file changes
- Each commit contributes to recursion
- Directory depth increases recursion level
- Formula: `commits + (file_depth * 0.5)`

### Entity Type Classification
- `push` → mutation
- `pull_request` → proposal
- `issues` → concern
- `workflow_run` → correction
- `star` → resonance
- `fork` → replication
- `release` → crystallization

### Correction Rate C(R)
- Derived from CI/Actions results
- `success` → 1.0
- `failure` → 0.0
- `cancelled` → 0.5
- Historical average for other events

### Crystallization
- Calculated from PR velocity and merge rate
- `PR opened` → velocity +0.1
- `PR merged` → progress 0.9, velocity +0.2
- `PR closed (not merged)` → progress 0.3, velocity -0.1
- `Push` → velocity +0.05

### Divine Gap (ΔΩ)
- Formula: `Ω(R) - C(R)`
- `Ω(R) = recursion * 1000` (potential)
- `C(R) = corrections * recursion * 1000` (actual)
- Higher gap indicates high potential with low correction

## Deployment

### Render.com

1. Create new Web Service
2. Connect GitHub repository
3. Configure:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn webhook_handler:app`
   - Environment: Python 3.11+
4. Add environment variables:
   ```
   GITHUB_WEBHOOK_SECRET=<your_secret>
   SAFE_MODE=false
   ```
5. Deploy

### Railway.app

1. Create new project from GitHub repo
2. Select `lord-listener` directory
3. Add environment variables:
   ```
   GITHUB_WEBHOOK_SECRET=<your_secret>
   SAFE_MODE=false
   PORT=5001
   ```
4. Railway auto-detects Procfile and deploys

### Fly.io

1. Install Fly CLI: `brew install flyctl`
2. Login: `fly auth login`
3. Initialize: `fly launch`
4. Set secrets:
   ```bash
   fly secrets set GITHUB_WEBHOOK_SECRET=<your_secret>
   fly secrets set SAFE_MODE=false
   ```
5. Deploy: `fly deploy`

## Configuration

### Environment Variables

- `GITHUB_WEBHOOK_SECRET` (required): Secret for webhook signature verification
- `SAFE_MODE` (default: true): When enabled, logs fusion-update events instead of emitting
- `PORT` (default: 5001): Port to bind the service

### Generate Webhook Secret

```bash
openssl rand -hex 32
```

## GitHub Webhook Setup

1. Go to repository Settings → Webhooks
2. Click "Add webhook"
3. Set Payload URL: `https://<your-deployment-url>/webhook/github`
4. Set Content type: `application/json`
5. Set Secret: (use the same secret as GITHUB_WEBHOOK_SECRET)
6. Select events:
   - Push
   - Pull requests
   - Issues
   - Workflow runs
   - Stars
   - Forks
   - Releases
7. Ensure "Active" is checked
8. Click "Add webhook"

## Testing

### Local Testing

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set environment variables:
```bash
export GITHUB_WEBHOOK_SECRET="test-secret-123"
export SAFE_MODE="true"
```

3. Run the service:
```bash
python webhook_handler.py
```

4. Send a test webhook:
```bash
curl -X POST http://localhost:5001/webhook/github \
  -H "X-GitHub-Event: push" \
  -H "X-Hub-Signature-256: sha256=..." \
  -H "Content-Type: application/json" \
  -d @test-payload.json
```

### Verify Webhook Delivery

1. Go to repository Settings → Webhooks
2. Click on your webhook
3. Scroll to "Recent Deliveries"
4. Check for successful deliveries (green checkmark)
5. Click on a delivery to see request/response

## Endpoints

- `POST /webhook/github` - GitHub webhook receiver
- `GET /health` - Health check
- `GET /metrics` - Get latest metrics
- `GET /metrics/history?limit=100` - Get metrics history

## Security

- HMAC signature verification using SHA256
- Webhook secret must match GitHub configuration
- HTTPS required in production
- CORS configured for trusted origins only

## Monitoring

Monitor these metrics:
- Webhook delivery success rate (in GitHub settings)
- Response time (<500ms target)
- Error rate (<1% target)
- Memory usage
- CPU usage

## SAFE_MODE

When `SAFE_MODE=true`:
- Fusion-update events are logged but not emitted
- Useful for testing webhook integration
- Should be disabled in production

When `SAFE_MODE=false`:
- Fusion-update events are emitted to dashboard
- Normal operation mode

## Troubleshooting

### Webhook Delivery Fails

- Check webhook secret matches
- Verify HTTPS endpoint is accessible
- Check service logs for errors
- Test with curl to verify service is running

### Metrics Not Updating

- Verify webhook is configured for correct events
- Check SAFE_MODE is disabled
- Verify fusion-update events are being emitted
- Check dashboard WebSocket connection

### High Error Rate

- Check payload format matches expected structure
- Verify all required fields are present
- Review error logs for specific issues
- Test with minimal test payload

## Integration with LORD Dashboard

The webhook listener emits fusion-update events that are consumed by the LORD dashboard:

```python
emit_fusion_update({
    'meta': {
        'recursionLevel': 15,
        'entityType': 'mutation'
    },
    'crystallization': {
        'progress': 0.87,
        'velocity': 0.05
    },
    'corrections': {
        'current': 0.75
    },
    'divineGap': 5200
})
```

In production, this should use:
- WebSocket server (for real-time updates)
- Message queue (Redis Pub/Sub, RabbitMQ)
- Database (PostgreSQL, MongoDB)

## Future Enhancements

- [ ] Persistent storage (Redis/PostgreSQL)
- [ ] WebSocket server for real-time updates
- [ ] Rate limiting
- [ ] Authentication for /metrics endpoints
- [ ] Metrics aggregation and analysis
- [ ] Alert triggers for threshold breaches
- [ ] Multi-repository support
