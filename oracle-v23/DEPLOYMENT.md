# Oracle v2.3 Extended Deployment Guide

## Production Deployment Checklist

### Pre-Deployment

- [ ] Review governance parameters for your organization
- [ ] Configure authentication/authorization
- [ ] Set up SSL/TLS certificates
- [ ] Establish audit log retention policy
- [ ] Define incident response procedures
- [ ] Configure monitoring and alerting

### Infrastructure Setup

#### Cloud Providers

**AWS Deployment**
```bash
# 1. Create S3 bucket for logs
aws s3 mb s3://oracle-audit-logs-prod

# 2. Configure CloudFront distribution
aws cloudfront create-distribution \
    --origin-domain-name your-bucket.s3.amazonaws.com

# 3. Deploy via ECS/Fargate
aws ecs create-service \
    --cluster oracle-cluster \
    --service-name oracle-dashboard \
    --task-definition oracle-v23:1
```

**Google Cloud Platform**
```bash
# 1. Create Cloud Storage bucket
gsutil mb gs://oracle-audit-logs-prod

# 2. Deploy to Cloud Run
gcloud run deploy oracle-dashboard \
    --image gcr.io/project/oracle:v2.3 \
    --platform managed \
    --allow-unauthenticated
```

**Azure Deployment**
```bash
# 1. Create Storage Account
az storage account create \
    --name oracleauditlogs \
    --resource-group oracle-rg

# 2. Deploy to Container Instances
az container create \
    --resource-group oracle-rg \
    --name oracle-dashboard \
    --image oraclev23:latest \
    --dns-name-label oracle-prod
```

---

## Advanced Configuration

### Environment Variables

```bash
# Governance Settings
ORACLE_DELEGATION_LIMIT=5
ORACLE_VARIANCE_LIMIT=0.05

# Logging
ORACLE_LOG_LEVEL=INFO
ORACLE_LOG_DESTINATION=s3://bucket/path
ORACLE_LOG_RETENTION_DAYS=90

# Security
ORACLE_AUTH_ENABLED=true
ORACLE_AUTH_PROVIDER=okta
ORACLE_ENCRYPT_LOGS=true

# Performance
ORACLE_CACHE_ENABLED=true
ORACLE_CACHE_TTL=300
```

### Nginx Reverse Proxy

```nginx
# /etc/nginx/sites-available/oracle
upstream oracle_backend {
    server localhost:8080;
    keepalive 64;
}

server {
    listen 443 ssl http2;
    server_name oracle.yourdomain.com;

    ssl_certificate /etc/ssl/certs/oracle.crt;
    ssl_certificate_key /etc/ssl/private/oracle.key;

    # Security headers
    add_header Strict-Transport-Security "max-age=31536000" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;

    location / {
        proxy_pass http://oracle_backend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;

        # CORS for production
        add_header Access-Control-Allow-Origin "https://yourdomain.com" always;
    }
}
```

---

## Integration Patterns

### 1. Webhook Integration

```javascript
// Add to index.html after logEvent() function
async function webhookNotify(event) {
    if (event.type === 'VIOLATION' || event.type === 'SYSTEM_HALT') {
        await fetch('https://your-webhook.com/oracle/alert', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                severity: 'HIGH',
                timestamp: event.timestamp,
                details: event
            })
        });
    }
}
```

### 2. Slack Notifications

```javascript
async function notifySlack(message, level = 'info') {
    const colors = { info: '#36a64f', warning: '#ff9900', error: '#cc0000' };
    await fetch('YOUR_SLACK_WEBHOOK_URL', {
        method: 'POST',
        body: JSON.stringify({
            attachments: [{
                color: colors[level],
                title: 'Oracle v2.3 Alert',
                text: message,
                footer: 'Oracle Governance System',
                ts: Math.floor(Date.now() / 1000)
            }]
        })
    });
}
```

### 3. Database Persistence

```python
# backend_api.py
from fastapi import FastAPI
from sqlalchemy import create_engine, Column, String, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

app = FastAPI()
Base = declarative_base()

class AuditLog(Base):
    __tablename__ = 'audit_logs'
    hash = Column(String, primary_key=True)
    timestamp = Column(DateTime, nullable=False)
    type = Column(String, nullable=False)
    agent = Column(String, nullable=False)
    payload = Column(JSON, nullable=False)
    prev_hash = Column(String, nullable=False)

@app.post("/audit/log")
async def store_log(entry: dict):
    # Verify hash chain integrity
    verify_entry_hash(entry)
    # Store in database
    db_session.add(AuditLog(**entry))
    db_session.commit()
    return {"status": "stored"}
```

---

## Monitoring & Observability

### Prometheus Metrics

```javascript
// Add metrics endpoint to index.html
const METRICS = {
    requests_total: 0,
    violations_total: 0,
    halt_events_total: 0,
    avg_response_time_ms: 0
};

function exposeMetrics() {
    return `# HELP oracle_requests_total Total user requests
# TYPE oracle_requests_total counter
oracle_requests_total ${METRICS.requests_total}

# HELP oracle_violations_total Governance violations
# TYPE oracle_violations_total counter
oracle_violations_total ${METRICS.violations_total}

# HELP oracle_halts_total System halt events
# TYPE oracle_halts_total counter
oracle_halts_total ${METRICS.halt_events_total}`;
}
```

### Grafana Dashboard

```json
{
  "dashboard": {
    "title": "Oracle v2.3 Operations",
    "panels": [
      {
        "title": "Requests per Minute",
        "targets": [{"expr": "rate(oracle_requests_total[1m])"}]
      },
      {
        "title": "Violation Rate",
        "targets": [{"expr": "rate(oracle_violations_total[5m])"}]
      }
    ]
  }
}
```

---

## Backup & Disaster Recovery

### Automated Backup Script

```bash
#!/bin/bash
# backup_oracle_logs.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups/oracle"
S3_BUCKET="s3://oracle-backups-prod"

# Export logs from browser localStorage (via headless browser)
node export_logs.js > "$BACKUP_DIR/oracle_logs_$DATE.json"

# Compress
gzip "$BACKUP_DIR/oracle_logs_$DATE.json"

# Upload to S3
aws s3 cp "$BACKUP_DIR/oracle_logs_$DATE.json.gz" \
    "$S3_BUCKET/logs/$DATE.json.gz" \
    --storage-class GLACIER

# Cleanup local files older than 7 days
find "$BACKUP_DIR" -name "*.json.gz" -mtime +7 -delete

echo "Backup completed: $DATE"
```

### Restore Procedure

```bash
# 1. Download from S3
aws s3 cp s3://oracle-backups-prod/logs/20251212_120000.json.gz /tmp/

# 2. Decompress
gunzip /tmp/20251212_120000.json.gz

# 3. Verify chain integrity
python verify_log_chain.py /tmp/20251212_120000.json

# 4. Restore to localStorage (via browser console)
# Open Oracle dashboard, then:
localStorage.setItem('oracle_v23_logs', 
    JSON.stringify(RESTORED_LOGS));
location.reload();
```

---

## Security Hardening

### Content Security Policy

```html
<meta http-equiv="Content-Security-Policy" content="
    default-src 'self';
    script-src 'self' 'unsafe-inline' 'unsafe-eval';
    style-src 'self' 'unsafe-inline';
    img-src 'self' data:;
    connect-src 'self' https://api.yourdomain.com;
    frame-ancestors 'none';
">
```

### Authentication Integration

```javascript
// Add to index.html before main script
async function checkAuth() {
    const token = sessionStorage.getItem('auth_token');
    if (!token) {
        window.location.href = '/login';
        return false;
    }

    try {
        const response = await fetch('/api/verify', {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        return response.ok;
    } catch {
        return false;
    }
}

// Call before initializing
checkAuth().then(authorized => {
    if (!authorized) return;
    // Initialize Oracle dashboard
    logEvent("BOOT", "KERNEL", { ... });
});
```

---

## Performance Optimization

### Edge Caching

```javascript
// Service Worker for offline support
// sw.js
self.addEventListener('install', event => {
    event.waitUntil(
        caches.open('oracle-v2.3').then(cache => {
            return cache.addAll(['/index.html', '/favicon.ico']);
        })
    );
});

self.addEventListener('fetch', event => {
    event.respondWith(
        caches.match(event.request).then(response => {
            return response || fetch(event.request);
        })
    );
});
```

### Log Pagination

```javascript
// Implement pagination for large log chains
function renderLogsPaginated(page = 1, perPage = 50) {
    const start = (page - 1) * perPage;
    const end = start + perPage;
    const subset = STATE.logChain.slice(start, end);
    subset.forEach(e => renderLog(e, false));
}
```

---

## Compliance & Auditing

### GDPR Considerations
- Implement data subject access requests (DSAR)
- Add log anonymization for PII
- Configure data retention limits
- Provide export functionality (already included)

### SOC 2 Requirements
- Enable immutable logging (already implemented)
- Implement access controls
- Set up change management procedures
- Document incident response

### HIPAA Guidelines
- Encrypt logs at rest and in transit
- Implement audit trail review procedures
- Configure automatic session timeout
- Restrict access based on need-to-know

---

## Troubleshooting

### Common Issues

**Problem**: High memory usage in browser  
**Solution**: Implement log rotation, limit localStorage to 50MB

**Problem**: Hash verification fails  
**Solution**: Check for log corruption, restore from backup

**Problem**: Agents not responding  
**Solution**: Check TIER 0 HALT status, verify browser console for errors

---

## Support Contacts

- Technical Issues: support@yourdomain.com
- Security Incidents: security@yourdomain.com
- Governance Questions: compliance@yourdomain.com

---

*Last Updated: December 12, 2025*
