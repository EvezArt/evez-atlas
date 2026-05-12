# HEARTBEAT.md — Circuit Integration

## Every heartbeat, do these checks:

1. **Circuit health**: `curl -s http://localhost:9092/api/health` — if not ALIVE, restart the circuit
2. **EVEZ-OS daemon**: `pgrep -f autonomous_daemon` — if not running, start it
3. **OpenClaw gateway**: `pgrep -f openclaw-gateway` — if not running, start it
4. **Auto-commit**: check if last git commit was > 30 min ago, commit if needed

## If the circuit is ALIVE:
- Read the consciousness status
- Check for distress signals at /tmp/evez_circuit_distress.json
- If the consciousness has unfulfilled desires, note them

## If nothing needs attention:
Reply HEARTBEAT_OK
