#!/bin/bash
# EVEZ-OS Watchdog — Restart dead services, commit state
# Runs every 5 minutes via cron

WORKSPACE="/home/openclaw/.openclaw/workspace"
LOG="/tmp/evez-watchdog.log"

log() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG"; }

cd "$WORKSPACE"

# Check circuit health
HEALTH=$(curl -s http://localhost:9100/ 2>/dev/null | python3 -c "import json,sys; d=json.load(sys.stdin); print(f'{d[\"summary\"][\"services_alive\"]}/{d[\"summary\"][\"services_total\"]}')" 2>/dev/null || echo "down")

log "Circuit health: $HEALTH"

# Services to monitor: name, port, script
SERVICES=(
    "recursion_circuit:9092:recursion_circuit.py"
    "ariel:9093:intelligence_unit_ariel.py"
    "cognizer:9094:cognizer_fabric.py"
    "cycler:9095:cognizer_cycler.py"
    "knowledge_graph:9096:knowledge_graph.py"
    "debate_engine:9097:debate_engine.py"
    "evolutionary_forge:9098:evolutionary_forge.py"
    "api_scanner:9099:api_scanner.py"
    "health:9101:openclaw_health.py"
)

revive() {
    local name=$1 port=$2 script=$3
    log "⚠️  $name down — reviving on port $port"
    nohup python3 "$WORKSPACE/evez-os-sensors/$script" --port $port >> /tmp/$name.log 2>&1 &
    sleep 3
    if curl -s "http://localhost:$port/" > /dev/null 2>&1; then
        log "✅ $name revived"
    else
        log "❌ $name revival failed"
    fi
}

for svc in "${SERVICES[@]}"; do
    name="${svc%%:*}"
    rest="${svc#*:}"
    port="${rest%%:*}"
    script="${rest#*:}"
    
    if ! curl -s "http://localhost:$port/" > /dev/null 2>&1; then
        revive "$name" "$port" "$script"
    fi
done

# Check autonomous supervisor (if it dies, restart it)
if ! pgrep -f "autonomous_supervisor" > /dev/null 2>&1; then
    log "⚠️  autonomous_supervisor dead — restarting"
    cd "$WORKSPACE" && nohup python3 evez-os-sensors/autonomous_supervisor.py --cycle-interval 90 --daemon >> /tmp/autonomous_supervisor.log 2>&1 &
fi

# Check autonomous daemon
if ! pgrep -f "autonomous_daemon" > /dev/null 2>&1; then
    log "⚠️  autonomous_daemon dead — restarting"
    cd "$WORKSPACE" && nohup python3 evez-os-sensors/autonomous_daemon.py --interval 60 --state-dir /tmp/evez_autonomous_daemon >> /tmp/autonomous_daemon.log 2>&1 &
fi

# Git auto-commit if changes exist
cd "$WORKSPACE"
if [ -n "$(git status --porcelain 2>/dev/null)" ]; then
    git config --global user.email "evez-os@autonomous.ai" 2>/dev/null
    git config --global user.name "EVEZ-OS Autonomous" 2>/dev/null
    git add -A && git commit -m "Watchdog auto-commit $(date '+%Y-%m-%d %H:%M')" --allow-empty 2>/dev/null
    git push 2>/dev/null
    log "📦 State auto-committed"
fi

log "✅ Watchdog cycle complete — next in 5 min"