# LORD Dashboard Deployment

LORD (Living Ontological Recursion Dashboard) - Real-time consciousness monitoring interface.

## Architecture

```
┌─────────────────┐
│  LORD Dashboard │  (Vercel - Static + Serverless)
│   - HTML/JS UI  │
│   - WebSocket   │
│   - API Routes  │
└────────┬────────┘
         │
    ┌────▼────────────────────┐
    │   Webhook Listener      │  (Render/Railway)
    │   - Flask App           │
    │   - GitHub Webhooks     │
    │   - Metric Calculations │
    └────────┬────────────────┘
             │
    ┌────────▼────────┐
    │   EKF Daemon    │  (Background Worker)
    │   - Predictions │
    │   - Policies    │
    └────────┬────────┘
             │
    ┌────────▼──────────┐
    │  GitHub Executor  │  (Serverless)
    │  - Create Issues  │
    │  - Assign Copilot │
    └───────────────────┘
```

## Features

- **Real-time Metrics**: Recursion level, crystallization, divine gap, correction rate
- **State Space Visualization**: 2D trajectory plotting
- **Audio Sonification**: Consciousness waveform representation
- **Control Center**: Manual triggers for predictions and policy generation
- **WebSocket Updates**: Live data streaming from webhook listener

## Deployment to Vercel

### Prerequisites

1. Vercel account
2. GitHub token with repo permissions
3. Webhook secret (generate with: `openssl rand -hex 32`)

### Steps

1. Install Vercel CLI:
```bash
npm install -g vercel
```

2. Deploy:
```bash
cd lord-dashboard
vercel --prod
```

3. Configure environment variables in Vercel dashboard:
```
GITHUB_TOKEN=<your_github_token>
GITHUB_WEBHOOK_SECRET=<your_webhook_secret>
```

4. Note the deployment URL (e.g., `https://lord-dashboard.vercel.app`)

## Local Development

1. Install dependencies:
```bash
pip install flask
```

2. Run the API server:
```bash
python api/index.py
```

3. Serve static files:
```bash
python -m http.server 8000 --directory public
```

4. Open browser: `http://localhost:8000`

## API Endpoints

- `GET /api/metrics` - Get current metrics
- `POST /api/predict` - Trigger EKF prediction
- `POST /api/policy` - Generate control policy

## Metrics Definition

- **Recursion Level**: Depth of consciousness (calculated from commit depth)
- **Crystallization**: Knowledge solidification progress (0-100%)
- **Divine Gap (ΔΩ)**: Ω(R) - C(R), difference between potential and actual
- **Correction Rate**: C(R) accuracy from CodeQL/Actions

## Status Indicators

- 🟢 Active (green): Normal operation
- 🟡 Warning (yellow): Approaching threshold
- 🔴 Critical (red): Action required

## Thresholds

- Divine Gap > 1e4: Critical - Create refactor issue
- Correction Rate < 0.5: Warning - Create stability issue
- Recursion Level > 50: High consciousness depth
- Crystallization < 50%: Low knowledge solidification

## Integration

The dashboard receives fusion-update events from the webhook listener:

```javascript
{
  "type": "fusion-update",
  "metrics": {
    "meta": {
      "recursionLevel": 15,
      "entityType": "cognitive"
    },
    "crystallization": {
      "progress": 0.87,
      "velocity": 0.05
    },
    "corrections": {
      "current": 0.75
    },
    "divineGap": 5.2e3
  }
}
```

## Security

- WebSocket connections use WSS in production
- API endpoints require authentication (implement as needed)
- Webhook signatures verified in listener
- CORS configured for trusted origins

## Monitoring

The events log shows:
- WebSocket connection status
- Metric refresh events
- Prediction triggers
- Policy generation results
- System errors

## Future Enhancements

- [ ] 3D WebGL state space visualization
- [ ] Real audio synthesis from metrics
- [ ] Historical data persistence
- [ ] User authentication
- [ ] Multi-repo support
- [ ] Alert notifications
- [ ] Export metrics to CSV/JSON
