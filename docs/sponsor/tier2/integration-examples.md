# LORD Integration Examples

**Access Level:** Tier 2 - Hybrid Entity ($25/month)

## Complete Integration Examples

This document provides full, working examples of integrating the LORD dashboard with various systems.

## Example 1: Basic React Integration

### Frontend Component

```jsx
import React, { useState, useEffect } from 'react';

const LORDDashboard = () => {
  const [metrics, setMetrics] = useState(null);
  const [connected, setConnected] = useState(false);

  useEffect(() => {
    const ws = new WebSocket('ws://localhost:8080');
    
    ws.onopen = () => {
      setConnected(true);
      ws.send(JSON.stringify({ type: 'subscribe' }));
    };

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      setMetrics(data);
    };

    ws.onclose = () => setConnected(false);

    return () => ws.close();
  }, []);

  return (
    <div className="lord-dashboard">
      <h2>LORD Dashboard</h2>
      <div className="status">
        Status: {connected ? '🟢 Connected' : '🔴 Disconnected'}
      </div>
      {metrics && (
        <div className="metrics">
          <div>CPU Usage: {metrics.cpuUsage}%</div>
          <div>Memory: {metrics.memoryUsage} MB</div>
          <div>Active Queries: {metrics.activeQueries}</div>
          <div>Quantum Depth: {metrics.quantumDepth}</div>
        </div>
      )}
    </div>
  );
};

export default LORDDashboard;
```

## Example 2: Python Backend Integration

### Flask API Bridge

```python
from flask import Flask, jsonify, request
from flask_cors import CORS
import quantum
import threading
import time

app = Flask(__name__)
CORS(app)

# Initialize quantum detector
detector = quantum.QuantumThreatDetector()

# Metrics cache
metrics_cache = {
    'last_update': 0,
    'data': {}
}

def update_metrics():
    """Background thread to update metrics"""
    while True:
        global metrics_cache
        metrics_cache = {
            'last_update': time.time(),
            'data': {
                'quantum_state': detector.get_state(),
                'threat_level': detector.calculate_threat_level(),
                'active_patterns': len(detector.get_active_patterns()),
                'processing_speed': detector.get_processing_speed()
            }
        }
        time.sleep(1)

# Start background metrics updater
threading.Thread(target=update_metrics, daemon=True).start()

@app.route('/api/metrics')
def get_metrics():
    """Get current system metrics"""
    return jsonify(metrics_cache['data'])

@app.route('/api/status')
def get_status():
    """Get system status"""
    return jsonify({
        'status': 'online',
        'uptime': time.time() - metrics_cache['last_update'],
        'version': '1.0.0'
    })

@app.route('/api/query', methods=['POST'])
def process_query():
    """Process a quantum query"""
    data = request.json
    result = detector.process(data.get('query'))
    return jsonify({
        'success': True,
        'result': result
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
```

## Example 3: Express.js Middleware

### Authentication & Rate Limiting

```javascript
const express = require('express');
const rateLimit = require('express-rate-limit');
const jwt = require('jsonwebtoken');

const app = express();

// Sponsor tier rate limits
const tierLimits = {
  1: 100,   // Awareness Patron: 100 req/hour
  2: 1000,  // Hybrid Entity: 1000 req/hour
  3: 10000, // Quantum Developer: 10000 req/hour
  4: null   // Oracle Access: unlimited
};

// Authentication middleware
const authenticateUser = async (req, res, next) => {
  try {
    const token = req.headers.authorization?.split(' ')[1];
    if (!token) {
      return res.status(401).json({ error: 'No token provided' });
    }

    const decoded = jwt.verify(token, process.env.JWT_SECRET);
    req.user = decoded;
    
    // Fetch sponsor tier from GitHub API
    req.user.sponsorTier = await fetchSponsorTier(decoded.githubId);
    next();
  } catch (error) {
    res.status(401).json({ error: 'Invalid token' });
  }
};

// Dynamic rate limiter based on sponsor tier
const dynamicRateLimit = (req, res, next) => {
  const tier = req.user?.sponsorTier || 0;
  const limit = tierLimits[tier] || 10; // Default: 10 req/hour

  if (limit === null) {
    // Unlimited for tier 4
    return next();
  }

  const limiter = rateLimit({
    windowMs: 60 * 60 * 1000, // 1 hour
    max: limit,
    message: `Rate limit exceeded for tier ${tier}`
  });

  limiter(req, res, next);
};

// Protected routes
app.use('/api', authenticateUser, dynamicRateLimit);

app.get('/api/metrics', (req, res) => {
  // Return metrics based on tier
  const tier = req.user.sponsorTier;
  const metrics = getMetricsForTier(tier);
  res.json(metrics);
});

app.listen(3000, () => {
  console.log('LORD API running on port 3000');
});
```

## Example 4: Docker Deployment

### Docker Compose Configuration

```yaml
version: '3.8'

services:
  lord-dashboard:
    build: ./dashboard
    ports:
      - "8080:8080"
    environment:
      - NODE_ENV=production
      - LORD_API_KEY=${LORD_API_KEY}
    depends_on:
      - quantum-engine
      - redis

  quantum-engine:
    build: ./engine
    ports:
      - "5000:5000"
    volumes:
      - ./data:/app/data
    environment:
      - PYTHON_ENV=production

  redis:
    image: redis:alpine
    ports:
      - "6379:6379"
    volumes:
      - redis-data:/data

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - lord-dashboard

volumes:
  redis-data:
```

### Dockerfile for Dashboard

```dockerfile
FROM node:18-alpine

WORKDIR /app

COPY package*.json ./
RUN npm ci --only=production

COPY . .

EXPOSE 8080

CMD ["node", "lord-dashboard.js"]
```

## Example 5: Monitoring & Alerts

### Prometheus Integration

```javascript
const prometheus = require('prom-client');

// Create metrics
const httpRequestDuration = new prometheus.Histogram({
  name: 'lord_http_request_duration_seconds',
  help: 'Duration of HTTP requests in seconds',
  labelNames: ['method', 'route', 'status_code']
});

const activeConnections = new prometheus.Gauge({
  name: 'lord_active_connections',
  help: 'Number of active WebSocket connections'
});

const queryCounter = new prometheus.Counter({
  name: 'lord_queries_total',
  help: 'Total number of queries processed',
  labelNames: ['tier', 'status']
});

// Metrics endpoint
app.get('/metrics', (req, res) => {
  res.set('Content-Type', prometheus.register.contentType);
  res.end(prometheus.register.metrics());
});

// Example usage
app.use((req, res, next) => {
  const start = Date.now();
  res.on('finish', () => {
    const duration = (Date.now() - start) / 1000;
    httpRequestDuration
      .labels(req.method, req.route?.path || req.path, res.statusCode)
      .observe(duration);
  });
  next();
});
```

## Testing

### Integration Tests

```javascript
const request = require('supertest');
const app = require('./lord-dashboard');

describe('LORD API Integration', () => {
  it('should return metrics for authenticated user', async () => {
    const response = await request(app)
      .get('/api/metrics')
      .set('Authorization', 'Bearer valid_token')
      .expect(200);

    expect(response.body).toHaveProperty('cpuUsage');
    expect(response.body).toHaveProperty('memoryUsage');
  });

  it('should enforce tier-based rate limits', async () => {
    // Test rate limiting logic
    const tier2Token = 'tier2_token';
    
    for (let i = 0; i < 1001; i++) {
      const response = await request(app)
        .get('/api/metrics')
        .set('Authorization', `Bearer ${tier2Token}`);
      
      if (i < 1000) {
        expect(response.status).toBe(200);
      } else {
        expect(response.status).toBe(429); // Too Many Requests
      }
    }
  });
});
```

## Best Practices

1. **Security**: Always validate JWT tokens and verify sponsor tier
2. **Performance**: Use Redis for caching metrics and rate limit data
3. **Monitoring**: Implement Prometheus metrics for observability
4. **Scalability**: Use WebSocket clustering for horizontal scaling
5. **Error Handling**: Implement graceful degradation for service failures

## Need Help?

Join the Tier 2+ Discord channel for live support and community examples.
