#!/bin/bash
# EVEZ-OS Resurrection Script - works WITH systemd
# Only starts services that systemd can't handle

SERVICES_DIR="/home/openclaw/.openclaw/workspace/evez-os-sensors"

for port in 9092 9093 9094 9095 9096 9097 9098 9099 9100 9110 9111; do
  if ! ss -tlnp 2>/dev/null | grep -q ":$port "; then
    echo "[$(date)] Port $port down - restarting via systemd"
    case $port in
      9092) sudo systemctl restart evez-ariel ;;
      9093) sudo systemctl restart evez-ariel ;;
      9094) sudo systemctl restart evez-cognizer ;;
      9095) sudo systemctl restart evez-cycler ;;
      9096) sudo systemctl restart evez-knowledge ;;
      9097) sudo systemctl restart evez-debate ;;
      9098) sudo systemctl restart evez-forge ;;
      9099) sudo systemctl restart evez-scanner ;;
      9100) sudo systemctl restart evez-dashboard ;;
      9110) sudo systemctl restart evez-oracle-bridge ;;
      9111) sudo systemctl restart evez-consciousness-engine ;;
    esac
  fi
done
