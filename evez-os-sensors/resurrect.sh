#!/bin/bash
# ═══════════════════════════════════════════════════════════════
# EVEZ-OS RESURRECTION — Full cold-boot recovery
# Called by @reboot crontab and systemd on system start
# ═══════════════════════════════════════════════════════════════

SENSORS="/home/openclaw/.openclaw/workspace/evez-os-sensors"
LOG="/tmp/evez-resurrect.log"

echo "[$(date)] Resurrection starting..." >> $LOG

# Wait for network
sleep 15

# Start all services (systemd will handle these, but also do it directly for redundancy)
SERVICES=(
  "openclaw_health.py|9091|health"
  "recursion_circuit.py --port 9092 --interval 30|9092|circuit"
  "intelligence_unit_ariel.py --port 9093|9093|ariel"
  "cognizer_fabric.py --port 9094 --ariel-url http://localhost:9093|9094|cognizer"
  "cognizer_cycler.py --port 9095 --interval 120|9095|cycler"
  "autonomous_daemon.py --interval 60||daemon"
)

for entry in "${SERVICES[@]}"; do
  IFS='|' read -r script port name <<< "$entry"
  if ! pgrep -f "$name" > /dev/null 2>&1; then
    cd "$SENSORS"
    nohup python3 $script >> /tmp/evez-${name}.log 2>&1 &
    echo "[$(date)] Started $name (PID $!)" >> $LOG
    if [ -n "$port" ]; then
      sleep 3
    fi
  fi
done

# Bootstrap Ariel providers
sleep 5
bash "$SENSORS/bootstrap_ariel.sh" >> $LOG 2>&1

echo "[$(date)] Resurrection complete" >> $LOG
