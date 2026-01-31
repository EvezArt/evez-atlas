#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

if [[ -f package.json ]]; then
  echo "📦 Installing Node dependencies..."
  npm ci
else
  echo "ℹ️  package.json not found; skipping npm ci."
fi

mkdir -p src/memory
if [[ ! -f src/memory/audit.jsonl ]]; then
  touch src/memory/audit.jsonl
fi

if [[ -f .env ]]; then
  set -a
  # shellcheck disable=SC1091
  source .env
  set +a
fi

if [[ -z "${SECRET_KEY:-}" ]]; then
  echo "🔐 SECRET_KEY not set. Generating a local dev secret..."
  SECRET_KEY="$(python - <<'PY'
import secrets
print(secrets.token_hex(32))
PY
)"
fi

export SECRET_KEY

echo "🧪 Running tests..."
pytest

echo "🚀 Starting causal chain server..."
uvicorn --app-dir src/api causal_chain_server:app --host 0.0.0.0 --port 8000 > /tmp/uvicorn.log 2>&1 &
SERVER_PID=$!
echo "$SERVER_PID" > /tmp/uvicorn.pid

cat <<EOF

✅ Server started (PID: $SERVER_PID)

Smoke tests:
  curl -H "X-API-Key: tier0_public" http://localhost:8000/legion-status
  curl -H "X-API-Key: tier3_director" http://localhost:8000/legion-status

Resolve awareness:
  curl -X POST http://localhost:8000/resolve-awareness \
    -H "X-API-Key: tier3_director" \
    -H "Content-Type: application/json" \
    -d '{"output_id":"output-001"}'

Logs:
  tail -f /tmp/uvicorn.log
EOF
