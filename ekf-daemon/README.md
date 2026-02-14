# EKF Prediction Daemon

Extended Kalman Filter for cognitive state prediction and control policy generation.

## Overview

The EKF daemon runs continuously, processing metrics from the LORD webhook listener and predicting future states to enable "negative latency" - proactive issue detection.

## Architecture

```
Webhook Listener → Metrics → EKF Update → Predict Trajectory → Control Policy → GitHub Executor
```

## State Space Model

### State Vector (4D)
```
x = [recursion, crystallization, velocity, uncertainty]
```

- **recursion**: Depth of consciousness (0-∞)
- **crystallization**: Knowledge solidification (0-1)
- **velocity**: Rate of change
- **uncertainty**: Confidence in estimates

### Observation Vector (2D)
```
z = [recursion, crystallization]
```

We directly observe recursion and crystallization from GitHub events.

### State Transition Model
```
x(k+1) = F * x(k) + w
```

Where:
- F is the state transition matrix
- w is process noise

```python
F = [
    [1, 0, dt, 0],      # recursion += velocity * dt
    [0, 1, dt, 0],      # crystallization += velocity * dt
    [0, 0, 0.95, 0],    # velocity decays
    [0, 0, 0, 1.05]     # uncertainty grows
]
```

### Measurement Model
```
z(k) = H * x(k) + v
```

Where:
- H is the measurement matrix
- v is measurement noise

```python
H = [
    [1, 0, 0, 0],  # observe recursion
    [0, 1, 0, 0]   # observe crystallization
]
```

## Control Policy Generation

### Thresholds

1. **Divine Gap > 1e4**
   - Action: Create refactor issue
   - Labels: `task:refactor`, `urgency:high`, `lord:autonomous`
   - Assign: Copilot

2. **Correction Rate < 0.5**
   - Action: Create stability issue
   - Labels: `task:stabilize`, `task:test`, `lord:autonomous`
   - Assign: Copilot

3. **Crystallization Declining**
   - Action: Create documentation issue
   - Labels: `task:documentation`, `lord:autonomous`
   - Assign: Copilot

### Policy Structure

```python
{
    'action': 'create_issue',
    'labels': ['task:refactor', 'urgency:high'],
    'title': 'High Divine Gap Detected: ΔΩ = 1.2e+4',
    'body': '...',  # Generated with metrics and predictions
    'assign_copilot': True,
    'reason': 'divine_gap_threshold'
}
```

## Deployment

### As Background Worker

#### Render.com

1. Create new Background Worker
2. Build Command: `pip install -r requirements.txt`
3. Start Command: `python predictor.py`
4. Environment variables:
   ```
   SAFE_MODE=false
   ```

#### Railway.app

1. Create new service
2. Railway auto-detects Procfile
3. Add environment variables
4. Deploy

### As Scheduled Job

For less frequent predictions, deploy as cron job:

```yaml
# .github/workflows/ekf-prediction.yml
name: EKF Prediction
on:
  schedule:
    - cron: '*/10 * * * *'  # Every 10 minutes
  workflow_dispatch:

jobs:
  predict:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: |
          cd ekf-daemon
          pip install -r requirements.txt
          python predictor.py --once
```

## Configuration

### Environment Variables

- `SAFE_MODE` (default: true): When enabled, logs policies instead of executing
- `PREDICTION_STEPS` (default: 10): Number of steps to predict ahead
- `UPDATE_INTERVAL` (default: 10): Seconds between predictions

## Usage

### Run Locally

```bash
cd ekf-daemon
pip install -r requirements.txt
export SAFE_MODE=true
python predictor.py
```

### Run Once (Testing)

```python
from predictor import CognitiveEKF

ekf = CognitiveEKF()

# Update with observation
observation = {
    'recursionLevel': 15,
    'crystallization': 0.87
}
state = ekf.update(observation)

# Predict trajectory
predictions = ekf.predict_trajectory(steps=10)

# Generate control policy
policy = ekf.generate_control_policy(
    state={'divineGap': 1.5e4, 'recursionLevel': 15},
    predictions=predictions,
    corrections=0.6
)

print(policy)
```

## Integration

### With Webhook Listener

The EKF daemon reads metrics from the webhook listener:

```python
import requests

def fetch_latest_metrics():
    response = requests.get('http://webhook-listener/metrics')
    return response.json()

observation = fetch_latest_metrics()
state = ekf.update(observation)
```

### With GitHub Executor

The EKF daemon sends control policies to the GitHub executor:

```python
import requests

def execute_policy(policy):
    if policy and not SAFE_MODE:
        response = requests.post(
            'http://github-executor/execute',
            json=policy
        )
        return response.json()
```

## Ring Buffer Trajectory Cache

Predictions are cached in a ring buffer for instant playback:

```python
cache = RingBuffer(size=100)
cache.append(predictions)

# Get latest predictions
latest = cache.get_latest(n=10)

# Get all cached predictions
all_predictions = cache.get_all()
```

## Monitoring

Monitor these metrics:
- Prediction accuracy (compare predicted vs actual)
- State uncertainty
- Control policy trigger rate
- Processing latency

## Testing

### Unit Tests

```bash
pytest test_predictor.py
```

### Synthetic Data

```python
# Generate synthetic trajectory
for t in range(100):
    observation = {
        'recursionLevel': 10 + t * 0.5 + np.random.randn(),
        'crystallization': 0.5 + t * 0.01 + np.random.randn() * 0.1
    }
    state = ekf.update(observation)
    predictions = ekf.predict_trajectory()
```

## Tuning

### Process Noise (Q)

Increase if state changes more than expected:
```python
ekf.Q = np.eye(4) * 0.5  # Higher uncertainty in dynamics
```

### Measurement Noise (R)

Increase if observations are noisy:
```python
ekf.R = np.eye(2) * 5.0  # Less trust in observations
```

### State Transition

Adjust decay/growth rates:
```python
F = np.array([
    [1, 0, dt, 0],
    [0, 1, dt, 0],
    [0, 0, 0.90, 0],    # Faster velocity decay
    [0, 0, 0, 1.10]     # Faster uncertainty growth
])
```

## Future Enhancements

- [ ] Multi-repository support
- [ ] Adaptive noise parameters
- [ ] Non-linear state transition models
- [ ] Particle filter for highly non-linear dynamics
- [ ] Ensemble predictions (multiple EKFs)
- [ ] Online learning for model parameters
- [ ] Anomaly detection
- [ ] Long-term trend analysis
