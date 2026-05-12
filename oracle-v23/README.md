# Oracle v2.3 Deployment Package

**Built:** December 12, 2025  
**Version:** 2.3.0  
**Session:** Enterprise-Grade Multi-Agent System

## Quick Start (Local)

### Option 1: Direct Browser
1. Open `index.html` in any modern browser (Chrome, Firefox, Edge)
2. The dashboard will run entirely client-side
3. Audit logs stored in browser localStorage

### Option 2: Python Server
```bash
python3 server.py
```
Then visit: http://localhost:8080

### Option 3: Docker
```bash
docker-compose up -d
```
Then visit: http://localhost:8080

---

## Architecture Overview

### Tier 0: Constitutional Constraints
- **Delegation Depth Limit**: Max recursive agent calls (default: 5)
- **Financial Variance Delta**: Max deviation threshold (default: 0.05)
- **Interruptibility**: Global system halt capability

### Core Components
1. **Meta-Prompt Architect**: Generates research briefs with governance constraints
2. **Execution Agents**: Specialized workers (Financial, Research, Analysis)
3. **RSI Engine**: Recursive Self-Improvement loop
4. **Immutable Logger**: SHA-256 hash-chained audit trail

### Data Persistence
- **Local**: Browser localStorage (10MB limit)
- **Export**: JSON audit log download
- **Cloud**: Optional backend integration (see `docker-compose.yml`)

---

## Configuration

### Governance Parameters (Runtime Adjustable)
```javascript
CONFIG = {
    delegationLimit: 5,        // Max agent nesting
    financialVarianceLimit: 0.05  // Max financial deviation
}
```

### Color Scheme (CSS Variables)
```css
--bg: #0d1117       /* Background */
--panel: #161b22    /* Panel background */
--accent: #58a6ff   /* Primary accent */
--success: #238636  /* Success state */
--danger: #da3633   /* Error state */
```

---

## Deployment Scenarios

### 1. Research Lab (Local)
- Use direct browser mode
- Export audit logs daily
- No internet required

### 2. Enterprise (Cloud)
- Deploy via Docker
- Integrate with existing auth (modify `server.py`)
- Set up log aggregation (e.g., ELK stack)

### 3. Compliance Environment
- Enable audit log auto-upload
- Configure immutable storage (AWS S3 + Glacier)
- Implement access controls

---

## Security Notes

### Audit Log Integrity
Each log entry contains:
- **Timestamp**: ISO 8601 format
- **Hash**: SHA-256 of `timestamp|type|agent|payload|prevHash`
- **PrevHash**: Links to previous entry (blockchain-style)

### Verification
```python
import hashlib

def verify_log_chain(logs):
    for i, entry in enumerate(logs):
        if i == 0:
            assert entry['prevHash'] == "0" * 64
        else:
            assert entry['prevHash'] == logs[i-1]['hash']

        data = f"{entry['timestamp']}|{entry['type']}|{entry['agent']}|{json.dumps(entry['payload'])}|{entry['prevHash']}"
        computed = hashlib.sha256(data.encode()).hexdigest()
        assert computed == entry['hash']
```

---

## Troubleshooting

### Issue: Canvas not rendering
**Solution**: Check browser console for WebGL errors. Fallback to 2D rendering is automatic.

### Issue: Logs not persisting
**Solution**: Check browser localStorage quota (10MB). Clear old sessions or export logs.

### Issue: System appears frozen
**Solution**: Check if TIER 0 HALT button is active. Click to resume operations.

---

## File Structure
```
oracle_v23_deployment/
├── index.html          # Main dashboard (single-file app)
├── server.py           # Python development server
├── docker-compose.yml  # Container orchestration
├── Dockerfile          # Container image spec
├── README.md           # This file
└── DEPLOYMENT.md       # Extended deployment guide
```

---

## Support & Maintenance

### Log Rotation
Logs are kept in memory. For production:
1. Download logs daily via UI button
2. Upload to secure storage
3. Clear localStorage periodically

### Updates
Replace `index.html` with new version. Logs persist across updates.

### Monitoring
Key metrics exposed via console:
```javascript
STATE.logChain.length   // Total events logged
STATE.config            // Current governance settings
STATE.halted            // System status
```

---

## License & Compliance

This system implements governance principles from:
- Oracle v2.3 Deployment Kit specification
- DCOP (Distributed Constrained Optimization Problems) framework
- Constitutional AI alignment patterns

**Disclaimer**: This is a demonstration system. Production deployment requires additional security hardening, authentication, and monitoring infrastructure.

---

## Next Steps

1. ✓ Open `index.html` in browser
2. ✓ Click "Inject Request" to see agent orchestration
3. ✓ Observe immutable log entries
4. ✓ Test TIER 0 HALT interrupt capability
5. ✓ Download audit log as JSON
6. → Integrate with your backend API
7. → Configure organizational policies
8. → Deploy to production environment

---

*Built with governance-first architecture. For technical questions, review the inline code comments in `index.html`.*
