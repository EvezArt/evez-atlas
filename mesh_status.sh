#!/bin/bash
# mesh_status.sh — Universal GCP Mesh Health Sweep (Peter Steinberger/Architect Level)
# Usage: bash mesh_status.sh [-v]                # add -v for verbose logs

NODES=(
  "gcp-west:34.53.51.34"
  "gcp-small:34.23.192.213"
  "gcp-openclaw:35.222.248.151"
  "gcp-power:136.113.102.152"
  "gcp-knot:136.118.144.227"
)
USER="openclaw"
KEY="$HOME/.ssh/openclaw-gcp"
GATEWAY_PORT=18789
API_PORT=18790

GREEN="\033[0;32m"
RED="\033[0;31m"
YELLOW="\033[0;33m"
NC="\033[0m"

printf "Mesh Status: $(date --utc)\n"
printf "%-14s %-8s %-8s %-10s %-8s %-8s %-8s %-8s %-8s\n" NODE CODE CFG GW_API MODEL TG CRON SPACE RESULT

for NODE in "${NODES[@]}"; do
  NAME="${NODE%%:*}"
  IP="${NODE##*:}"
  OUT=$(ssh -i "$KEY" -o ConnectTimeout=8 "$USER@$IP" 'bash -s' <<'ENDSSH'
cd ~/openclaw 2>/dev/null || cd ~
# 1. Git code up-to-date?
git_output=$(git status --porcelain 2>/dev/null)
test -z "$git_output" && echo "code:OK" || echo "code:STALE"
# 2. Config valid?
openclaw config validate >/dev/null 2>&1 && echo "cfg:OK" || echo "cfg:BAD"
# 3. Gateway 200?
curl -sf http://localhost:18789/ >/dev/null && echo "gw:OK" || echo "gw:DOWN"
# 4. API 200?
curl -sf http://localhost:18790/api/status >/dev/null && echo "api:OK" || echo "api:DOWN"
# 5. Model up? (ollama model list)
ollama list 2>/dev/null | grep -q evez && echo "model:OK" || echo "model:NONE"
# 6. Telegram bot?
pgrep -fa telegram | grep -q python && echo "tg:OK" || echo "tg:OFF"
# 7. Cron present?
crontab -l | grep -q openclaw && echo "cron:OK" || echo "cron:MISSING"
# 8. Disk space?
df_out=$(df -h / | awk "NR==2{print $5}")
(( $(echo "${df_out%%%}" | awk '{print ($1 < 90)?1:0}') )) && echo "space:OK" || echo "space:FULL"
ENDSSH
)
# Parse OUT
CODE=$(echo "$OUT" | grep code: | cut -d: -f2)
CFG=$(echo "$OUT" | grep cfg: | cut -d: -f2)
GW=$(echo "$OUT" | grep gw: | cut -d: -f2)
API=$(echo "$OUT" | grep api: | cut -d: -f2)
MODEL=$(echo "$OUT" | grep model: | cut -d: -f2)
TG=$(echo "$OUT" | grep tg: | cut -d: -f2)
CRON=$(echo "$OUT" | grep cron: | cut -d: -f2)
SPACE=$(echo "$OUT" | grep space: | cut -d: -f2)
RESULT=GREEN
for FIELD in $CODE $CFG $GW $API $MODEL $TG $CRON $SPACE; do
  [[ "$FIELD" != "OK" ]] && { RESULT=RED; break; }
done

if [[ $1 == "-v" ]]; then echo "=== $NAME ==="; echo "$OUT"; fi
COLOR=$([[ $RESULT == GREEN ]] && echo $GREEN || echo $RED)
printf "%-14s %-8s %-8s %-10s %-8s %-8s %-8s %-8s %-8s%s${NC}\n" "$NAME" "$CODE" "$CFG" "$GW/$API" "$MODEL" "$TG" "$CRON" "$SPACE" "$RESULT"
done
echo "DONE"
