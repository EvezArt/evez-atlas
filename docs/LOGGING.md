# Logging Conventions

This document defines logging standards and conventions for the Evez666 repository.

## Overview

Consistent logging is essential for debugging, monitoring, and auditing system behavior. All components should follow these conventions.

## Log Levels

### Console Logging

Use appropriate log levels for different types of messages:

- **`console.log()`**: Normal informational messages
- **`console.info()`**: Important information (skill loaded, service started)
- **`console.warn()`**: Warnings (missing optional config, deprecations)
- **`console.error()`**: Errors (exceptions, failures)
- **`console.debug()`**: Debug information (only when DEBUG=true)

### Python Logging

Use the standard `logging` module with these levels:

```python
import logging

logging.debug("Detailed information for diagnosing problems")
logging.info("Confirmation that things are working as expected")
logging.warning("An indication that something unexpected happened")
logging.error("A serious problem occurred")
logging.critical("A very serious error that may cause termination")
```

## Log Format Standards

### JavaScript/Node.js

**Skill logs:**
```javascript
console.log('[SkillName] Message here');
console.warn('[SkillName] Warning message');
console.error('[SkillName] Error:', error.message);
```

**SAFE_MODE logs:**
```javascript
console.log('[SAFE_MODE] Action logged but not executed:', data);
```

**Structured logs:**
```javascript
const logData = {
  timestamp: new Date().toISOString(),
  level: 'info',
  service: 'skill-name',
  event: 'action_performed',
  data: { ... }
};
console.log(JSON.stringify(logData));
```

### Python

**Standard format:**
```python
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

logger = logging.getLogger(__name__)
logger.info("Service started")
```

**Structured logs:**
```python
import json

log_data = {
    'timestamp': datetime.now().isoformat(),
    'level': 'info',
    'service': 'service-name',
    'event': 'action_performed',
    'data': {...}
}
logger.info(json.dumps(log_data))
```

## Log Locations

### GitHub Actions Workflows

Logs are automatically captured by GitHub Actions and available in:
- **UI:** Actions tab → Select workflow run → View logs
- **CLI:** `gh run view <run-id> --log`

No custom log files needed for workflows.

### OpenClaw Skills

Skills should log to stdout/stderr. OpenClaw captures these automatically.

**Optional log files:**
```bash
# Create logs directory if needed
mkdir -p logs/

# Skills can optionally write to files
logs/self-awareness.log
logs/deepclaw.log
logs/orchestrator.log
```

### Python Services

Python services should log to both console and optional files:

```python
import logging
from logging.handlers import RotatingFileHandler

# Console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

# File handler (optional)
file_handler = RotatingFileHandler(
    'logs/service.log',
    maxBytes=10*1024*1024,  # 10MB
    backupCount=5
)
file_handler.setLevel(logging.DEBUG)

# Configure logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(console_handler)
logger.addHandler(file_handler)
```

### Application Logs

Application-specific logs should go in:
```
logs/
├── app.log              # Main application log
├── errors.log           # Error-only log
├── access.log           # Access/request log (if applicable)
└── [service-name].log   # Service-specific logs
```

### Metrics and Data Logs

Structured data and metrics should go in:
```
data/
├── metrics/
│   ├── latest.json      # Current metrics snapshot
│   └── history/         # Historical metrics
├── events/
│   └── [date].jsonl     # Event logs (JSON Lines format)
└── logs/
    └── [date].log       # Archived logs by date
```

## SAFE_MODE Logging

When `SAFE_MODE=true` (default), all potentially side-effecting operations must log but not execute:

```javascript
if (process.env.SAFE_MODE !== 'false') {
  console.log('[SAFE_MODE] Action would be executed:', {
    action: 'create_issue',
    params: { title, body, repo }
  });
  return { safeMode: true, action: 'create_issue' };
}

// Execute actual action only when SAFE_MODE=false
await actuallyCreateIssue();
```

## Sensitive Data

**Never log sensitive data:**
- API keys
- Passwords
- Tokens
- Personal information
- Private repository content

**Redact sensitive data:**
```javascript
// Bad
console.log('API Key:', apiKey);

// Good
console.log('API Key:', apiKey ? '***' + apiKey.slice(-4) : 'not set');

// Better
const redactedKey = apiKey ? `${apiKey.substring(0, 7)}...${apiKey.slice(-4)}` : 'not set';
console.log('API Key:', redactedKey);
```

## Structured Logging Format

For machine-readable logs, use this JSON structure:

```javascript
{
  "timestamp": "2026-02-14T04:16:57.143Z",
  "level": "info|warn|error|debug",
  "service": "skill-name|workflow-name|service-name",
  "event": "event_type",
  "message": "Human-readable message",
  "data": {
    // Event-specific data
  },
  "context": {
    "environment": "production|development|test",
    "safeMode": true|false,
    "version": "1.0.0"
  }
}
```

## Performance Logging

For performance monitoring:

```javascript
const startTime = Date.now();

// ... operation ...

const duration = Date.now() - startTime;
console.log(`[Performance] ${operationName} completed in ${duration}ms`);

// Structured version
console.log(JSON.stringify({
  timestamp: new Date().toISOString(),
  level: 'info',
  event: 'performance_metric',
  operation: operationName,
  duration_ms: duration
}));
```

## Error Logging

Always include stack traces for errors:

```javascript
try {
  // ... code ...
} catch (error) {
  console.error('[Service] Error occurred:', error.message);
  console.error('Stack trace:', error.stack);
  
  // Structured version
  console.error(JSON.stringify({
    timestamp: new Date().toISOString(),
    level: 'error',
    service: 'service-name',
    event: 'error_occurred',
    error: {
      message: error.message,
      stack: error.stack,
      type: error.constructor.name
    }
  }));
}
```

## Audit Logging

For security-sensitive operations, maintain audit logs:

```javascript
const auditLog = {
  timestamp: new Date().toISOString(),
  actor: process.env.USER || 'system',
  action: 'create_issue',
  resource: {
    type: 'github_issue',
    repo: 'owner/repo',
    id: issueNumber
  },
  result: 'success|failure',
  metadata: {
    safeMode: process.env.SAFE_MODE !== 'false',
    ipAddress: '...',  // if available
  }
};

// Write to audit log file
fs.appendFileSync('logs/audit.jsonl', JSON.stringify(auditLog) + '\n');
```

## Log Rotation

For long-running services, implement log rotation:

### Node.js

Use `rotating-file-stream` package:

```javascript
const rfs = require('rotating-file-stream');

const stream = rfs.createStream('access.log', {
  interval: '1d',      // Rotate daily
  maxFiles: 7,         // Keep 7 days
  path: './logs',
  compress: 'gzip'     // Compress old logs
});
```

### Python

Use `RotatingFileHandler` or `TimedRotatingFileHandler`:

```python
from logging.handlers import TimedRotatingFileHandler

handler = TimedRotatingFileHandler(
    'logs/service.log',
    when='midnight',
    interval=1,
    backupCount=7
)
```

## Viewing Logs

### Real-time monitoring

```bash
# Tail logs
tail -f logs/app.log

# Follow with grep
tail -f logs/app.log | grep ERROR

# Multiple logs
tail -f logs/*.log
```

### Searching logs

```bash
# Search for errors
grep ERROR logs/app.log

# Search with context
grep -C 5 "error message" logs/app.log

# Search in multiple files
grep -r "pattern" logs/

# Search JSON logs
jq 'select(.level == "error")' logs/structured.jsonl
```

### GitHub Actions logs

```bash
# List recent runs
gh run list

# View specific run
gh run view <run-id>

# Download logs
gh run download <run-id>
```

## Best Practices

1. **Be Consistent**: Use the same format across all services
2. **Be Descriptive**: Include context in messages
3. **Be Structured**: Use JSON for machine parsing
4. **Be Secure**: Never log sensitive data
5. **Be Efficient**: Don't log excessively in hot paths
6. **Be Helpful**: Include enough info to debug issues
7. **Be SAFE**: Always respect SAFE_MODE

## Example: Complete Logging Setup

```javascript
// logger.js - Centralized logger module
const fs = require('fs');
const path = require('path');

class Logger {
  constructor(serviceName) {
    this.serviceName = serviceName;
    this.safeMode = process.env.SAFE_MODE !== 'false';
  }

  _format(level, message, data = {}) {
    return JSON.stringify({
      timestamp: new Date().toISOString(),
      level,
      service: this.serviceName,
      message,
      safeMode: this.safeMode,
      ...data
    });
  }

  _write(level, message, data) {
    const formatted = this._format(level, message, data);
    
    // Console output
    const consoleFn = console[level] || console.log;
    consoleFn(formatted);
    
    // Optional file output
    if (process.env.LOG_TO_FILE === 'true') {
      const logDir = path.join(process.cwd(), 'logs');
      if (!fs.existsSync(logDir)) {
        fs.mkdirSync(logDir, { recursive: true });
      }
      fs.appendFileSync(
        path.join(logDir, `${this.serviceName}.log`),
        formatted + '\n'
      );
    }
  }

  info(message, data) { this._write('info', message, data); }
  warn(message, data) { this._write('warn', message, data); }
  error(message, data) { this._write('error', message, data); }
  debug(message, data) {
    if (process.env.DEBUG === 'true') {
      this._write('debug', message, data);
    }
  }
}

module.exports = Logger;
```

**Usage:**
```javascript
const Logger = require('./logger');
const logger = new Logger('my-service');

logger.info('Service started', { version: '1.0.0' });
logger.warn('Configuration missing', { key: 'API_KEY' });
logger.error('Operation failed', { error: error.message });
```

---

*For questions or suggestions, see [TROUBLESHOOTING.md](TROUBLESHOOTING.md)*
