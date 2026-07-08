#!/usr/bin/env bash
#
# EVEZ OpenClaw — Gateway Token Extractor + Device Approver
# ═════════════════════════════════════════════════════════════════
#
# Run this ON EACH GCP NODE (via Cloud Shell SSH or browser terminal).
# It will:
#   1. Find and print the gateway token
#   2. Show the webchat URL with token
#   3. Approve any pending device pairings
#   4. Print the admin password if set
#
set -e

echo ""
echo "  ╔═══════════════════════════════════════════════════════════╗"
echo "  ║  EVEZ OpenClaw Gateway — Token & Pairing Fix              ║"
echo "  ╚═══════════════════════════════════════════════════════════╝"
echo ""

# ─── 1. FIND GATEWAY TOKEN ────────────────────────────────────────

echo "  [1/4] Searching for gateway token..."
echo ""

TOKEN=""
PASSWORD=""

# Check common locations
LOCATIONS=(
  "$HOME/.openclaw/openclaw.json"
  "$HOME/.openclaw/config.json"
  "$HOME/.config/openclaw/config.json"
  "/etc/openclaw/config.json"
  "/opt/openclaw/config.json"
  "/opt/openclaw/.env"
  "/opt/evez-openclaw/deploy/.env"
  "$HOME/.openclaw/.env"
  "$HOME/openclaw/.env"
)

for loc in "${LOCATIONS[@]}"; do
  if [ -f "$loc" ]; then
    echo "  Found: $loc"
    
    # Try to extract token
    t=$(grep -oP '(?:gateway_?token|GATEWAY_TOKEN|token|TOKEN|auth_?token)\s*[=:]\s*["'"'"']?([A-Za-z0-9_\-\.]+)' "$loc" 2>/dev/null | head -1 | grep -oP '[A-Za-z0-9_\-\.]+$' || true)
    if [ -n "$t" ]; then
      TOKEN="$t"
      echo "  → Token: $TOKEN"
    fi
    
    # Try to extract password
    p=$(grep -oP '(?:password|PASSWORD|admin_?password|ADMIN_PASSWORD)\s*[=:]\s*["'"'"']?([^\s"'"'"']+)' "$loc" 2>/dev/null | head -1 | grep -oP '[^\s"'"'"']+$' || true)
    if [ -n "$p" ]; then
      PASSWORD="$p"
      echo "  → Password: $PASSWORD"
    fi
    
    # Also try JSON parsing
    if command -v python3 >/dev/null 2>&1; then
      jt=$(python3 -c "import json; d=json.load(open('$loc')); print(d.get('token',d.get('gatewayToken',d.get('auth',{}).get('token',''))))" 2>/dev/null || true)
      if [ -n "$jt" ] && [ "$jt" != "None" ] && [ "$jt" != "" ]; then
        TOKEN="$jt"
        echo "  → Token (from JSON): $TOKEN"
      fi
    fi
    echo ""
  fi
done

# Check environment variables
if [ -z "$TOKEN" ]; then
  echo "  Checking environment variables..."
  if [ -n "$OPENCLAW_TOKEN" ]; then
    TOKEN="$OPENCLAW_TOKEN"
    echo "  → OPENCLAW_TOKEN: $TOKEN"
  elif [ -n "$GATEWAY_TOKEN" ]; then
    TOKEN="$GATEWAY_TOKEN"
    echo "  → GATEWAY_TOKEN: $TOKEN"
  fi
fi

# Try running openclaw CLI to get token
if [ -z "$TOKEN" ]; then
  echo ""
  echo "  Trying openclaw CLI..."
  if command -v openclaw >/dev/null 2>&1; then
    TOKEN=$(openclaw config get token 2>/dev/null || openclaw gateway token 2>/dev/null || true)
    if [ -n "$TOKEN" ]; then
      echo "  → CLI token: $TOKEN"
    fi
  fi
fi

# Check systemd service environment
if [ -z "$TOKEN" ]; then
  echo ""
  echo "  Checking systemd service..."
  for svc in openclaw openclaw-gateway evez-openclaw; do
    if systemctl list-units --all | grep -q "$svc"; then
      svc_env=$(systemctl show "$svc" -p Environment 2>/dev/null || true)
      t=$(echo "$svc_env" | grep -oP 'TOKEN=[^\s]+' | head -1 | cut -d= -f2 || true)
      if [ -n "$t" ]; then
        TOKEN="$t"
        echo "  → Service $svc token: $TOKEN"
      fi
    fi
    if systemctl --user list-units --all 2>/dev/null | grep -q "$svc"; then
      svc_env=$(systemctl --user show "$svc" -p Environment 2>/dev/null || true)
      t=$(echo "$svc_env" | grep -oP 'TOKEN=[^\s]+' | head -1 | cut -d= -f2 || true)
      if [ -n "$t" ]; then
        TOKEN="$t"
        echo "  → User service $svc token: $TOKEN"
      fi
    fi
  done
fi

if [ -z "$TOKEN" ]; then
  echo ""
  echo "  ⚠️  Token not found in standard locations."
  echo "  Run these manually to find it:"
  echo "    find / -name 'openclaw*' -type f 2>/dev/null | head -20"
  echo "    find / -name '.env' -type f 2>/dev/null | head -10"
  echo "    cat ~/.openclaw/* 2>/dev/null"
  echo "    env | grep -i token"
  echo "    env | grep -i openclaw"
else
  echo ""
  echo "  ✅ Gateway Token: $TOKEN"
fi

if [ -n "$PASSWORD" ]; then
  echo "  ✅ Admin Password: $PASSWORD"
fi

# ─── 2. SHOW WEBCAT URL WITH TOKEN ────────────────────────────────

echo ""
echo "  [2/4] Webchat URL (paste token in Settings):"
echo ""
THIS_IP=$(hostname -I 2>/dev/null | awk '{print $1}' || curl -s ifconfig.me 2>/dev/null || echo "YOUR_IP")
echo "  http://$THIS_IP:18789/chat?session=main"
echo ""
echo "  In the webchat UI:"
echo "    1. Open Settings (gear icon)"
echo "    2. Paste gateway token: $TOKEN"
echo "    3. Save and reconnect"

# ─── 3. APPROVE PENDING DEVICE PAIRINGS ───────────────────────────

echo ""
echo "  [3/4] Checking for pending device pairings..."
echo ""

if command -v openclaw >/dev/null 2>&1; then
  pending=$(openclaw pairing list 2>/dev/null || true)
  if [ -n "$pending" ]; then
    echo "  Pending pairings:"
    echo "$pending"
    echo ""
    
    # Auto-approve all pending
    request_ids=$(echo "$pending" | grep -oP '[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}' || true)
    if [ -n "$request_ids" ]; then
      echo "  Approving all pending pairings..."
      for rid in $request_ids; do
        openclaw pairing approve "$rid" 2>/dev/null && echo "  ✅ Approved: $rid" || echo "  ❌ Failed: $rid"
      done
    fi
  else
    echo "  No pending pairings found."
  fi
  
  # Also approve by Telegram code
  echo ""
  echo "  Approving Telegram pairing VKZK9B74..."
  openclaw pairing approve telegram VKZK9B74 2>/dev/null && echo "  ✅ Telegram pairing approved" || echo "  ⚠️  Could not approve (may not be pending)"
else
  echo "  openclaw CLI not found. Trying docker..."
  if command -v docker >/dev/null 2>&1; then
    docker exec openclaw openclaw pairing list 2>/dev/null || true
    docker exec openclaw openclaw pairing approve telegram VKZK9B74 2>/dev/null || true
  fi
fi

# ─── 4. GENERATE NEW TOKEN IF NEEDED ──────────────────────────────

if [ -z "$TOKEN" ]; then
  echo ""
  echo "  [4/4] Generating new gateway token..."
  if command -v openclaw >/dev/null 2>&1; then
    NEW_TOKEN=$(openclaw gateway reset-token 2>/dev/null || openclaw config set token "$(openssl rand -hex 24)" 2>/dev/null || true)
    if [ -n "$NEW_TOKEN" ]; then
      echo "  ✅ New token: $NEW_TOKEN"
      echo "  Save this! You'll need it for the webchat UI."
    fi
  else
    NEW_TOKEN=$(openssl rand -hex 24 2>/dev/null || python3 -c "import secrets; print(secrets.token_hex(24))" 2>/dev/null || echo "GENERATE_MANUALLY")
    echo "  Generated token: $NEW_TOKEN"
    echo "  Add this to your OpenClaw config to use it."
  fi
fi

echo ""
echo "  ════════════════════════════════════════════════════════════"
echo "  DONE — Copy the token above and paste it into the webchat"
echo "  Settings on your Samsung Galaxy A16."
echo "  ════════════════════════════════════════════════════════════"
echo ""
