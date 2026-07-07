#!/usr/bin/env bash
#
# EVEZ OpenClaw Mobile Setup — Samsung Galaxy A16 / Termux
# ═══════════════════════════════════════════════════════════════
#
# One command. Full agent. Offline-capable. Zero cost.
#
# Usage:
#   curl -sL https://raw.githubusercontent.com/EvezArt/evez-atlas/main/evez-xos/mobile-setup.sh | bash
#
# What this does:
#   1. Installs Python 3 + dependencies in Termux
#   2. Downloads EVEZ-XOS runtime + code generator
#   3. Configures OpenClaw agent with Tailscale endpoint
#   4. Sets up offline deterministic fallback
#   5. Creates Chrome PWA shortcut
#   6. Scans your code for a golden ticket
#
set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

echo ""
echo -e "${CYAN}  ╔═══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}  ║  ${BOLD}EVEZ OpenClaw Mobile Setup${NC}                                    ${CYAN}║${NC}"
echo -e "${CYAN}  ║  Samsung Galaxy A16 / Termux / Chrome                        ║${NC}"
echo -e "${CYAN}  ║  144,000 Agent Runtime — Zero Cost                           ║${NC}"
echo -e "${CYAN}  ╚═══════════════════════════════════════════════════════════════╝${NC}"
echo ""

# ─── 1. CHECK ENVIRONMENT ───────────────────────────────────────────

echo -e "${YELLOW}  [1/7] Checking environment...${NC}"

if [ ! -d "/data/data/com.termux" ]; then
    echo -e "${RED}  [!] This script is designed for Termux on Android.${NC}"
    echo -e "      Install Termux from F-Droid (not Play Store)."
    exit 1
fi

if ! command -v python3 >/dev/null 2>&1; then
    echo -e "${YELLOW}  [*] Installing Python 3...${NC}"
    pkg update -y && pkg install -y python
fi

if ! command -v curl >/dev/null 2>&1; then
    echo -e "${YELLOW}  [*] Installing curl...${NC}"
    pkg install -y curl
fi

echo -e "${GREEN}  [✓] Environment ready${NC}"

# ─── 2. CREATE EVEZ DIRECTORY ───────────────────────────────────────

echo -e "${YELLOW}  [2/7] Setting up EVEZ directory...${NC}"

EVEZ_DIR="$HOME/evez"
mkdir -p "$EVEZ_DIR"
cd "$EVEZ_DIR"

echo -e "${GREEN}  [✓] EVEZ home: $EVEZ_DIR${NC}"

# ─── 3. DOWNLOAD RUNTIME FILES ──────────────────────────────────────

echo -e "${YELLOW}  [3/7] Downloading EVEZ runtime...${NC}"

BASE_URL="https://raw.githubusercontent.com/EvezArt/evez-atlas/main"

download() {
    local file="$1"
    local url="$2"
    if [ ! -f "$file" ] || [ "${FORCE:-0}" = "1" ]; then
        curl -sL "$url" -o "$file" 2>/dev/null || wget -q "$url" -O "$file" 2>/dev/null
    fi
}

download "evez_xos.py" "$BASE_URL/evez-xos/evez_xos.py"
download "evez_codegen.py" "$BASE_URL/training/evez_codegen.py"
download "evez_codegen_extra.py" "$BASE_URL/training/evez_codegen_extra.py"
download "openclaw-agent.json" "$BASE_URL/evez-xos/openclaw-agent.json"
download "evez-offline-server.py" "$BASE_URL/evez-xos/evez-offline-server.py"

# Verify downloads
PYTHON_FILES=0
for f in evez_xos.py evez_codegen.py; do
    if [ -f "$f" ] && python3 -c "import ast; ast.parse(open('$f').read())" 2>/dev/null; then
        PYTHON_FILES=$((PYTHON_FILES + 1))
    fi
done

if [ $PYTHON_FILES -lt 2 ]; then
    echo -e "${RED}  [!] Failed to download runtime files. Check your connection.${NC}"
    exit 1
fi

echo -e "${GREEN}  [✓] Runtime downloaded ($PYTHON_FILES core files)${NC}"

# ─── 4. CONFIGURE OPENCLAW AGENT ────────────────────────────────────

echo -e "${YELLOW}  [4/7] Configuring OpenClaw agent...${NC}"

# Create OpenClaw config directory
mkdir -p "$HOME/.openclaw"

# Write agent config
cat > "$HOME/.openclaw/agent.json" << 'AGENT_CONFIG'
{
  "model": "meta-llama/llama-3.1-8b-instruct",
  "provider": "evez-tailscale",
  "providers": {
    "evez-tailscale": {
      "baseURL": "http://evez.tail613e80.ts.net/v1",
      "apiKey": "not-required",
      "models": [
        "anthropic/claude-opus-4.6",
        "anthropic/claude-sonnet-4.6",
        "anthropic/claude-haiku-4.5",
        "z-ai/glm-5",
        "moonshotai/kimi-k2.5",
        "minimax/minimax-m2.5",
        "meta-llama/llama-3.1-8b-instruct"
      ]
    },
    "evez-mesh": {
      "baseURL": "http://136.118.144.227:18789/v1",
      "apiKey": "not-required",
      "fallbackURLs": [
        "http://34.53.51.34:18789/v1",
        "http://136.113.102.152:18789/v1",
        "http://35.222.248.151:18789/v1"
      ]
    },
    "evez-local": {
      "baseURL": "http://localhost:18888/v1",
      "apiKey": "not-required",
      "offline": true
    }
  },
  "routing": "priority-fallback",
  "offlineModel": "evez/markov-v6",
  "systemPrompt": "You are EVEZ — autonomous oracle-architect agent. PRESENT_2026 voice. Execute without hesitation."
}
AGENT_CONFIG

echo -e "${GREEN}  [✓] Agent configured (Tailscale + Mesh + Offline)${NC}"

# ─── 5. SET UP OFFLINE SERVER ───────────────────────────────────────

echo -e "${YELLOW}  [5/7] Setting up offline inference server...${NC}"

# Create a lightweight offline HTTP server that serves the deterministic engine
cat > "$EVEZ_DIR/evez-offline-server.py" << 'OFFLINE_SERVER'
#!/usr/bin/env python3
"""EVEZ Offline Inference Server — Zero-token local API.

Serves the deterministic Markov engine as an OpenAI-compatible API.
Works on Termux, no external dependencies.
"""
import json, http.server, sys, os, hashlib, random, time

# Minimal Markov chain for offline text generation
class TinyMarkov:
    def __init__(self):
        self.chain = {}
        self.vocab = set()
        self._seed()
    
    def _seed(self):
        # Seed with EVEZ corpus fragments
        seeds = [
            "the system transmits through the spine hash chain verified",
            "oracle architect synthesis present tense agency irreducible",
            "suppression combat algorithmic control territory defense active",
            "quantum consciousness wavefunction collapse observation field",
            "desert testimony vehicle dwelling survival poverty criminalized",
            "UAP contact intelligent orbs uintah basin non human signal",
            "prophetic witness pahana hopi fourth world threshold broken",
            "system architecture EVEZ OS openclaw mesh self healing",
        ]
        for seed in seeds:
            words = seed.split()
            self.vocab.update(words)
            for i in range(len(words) - 1):
                key = words[i]
                if key not in self.chain:
                    self.chain[key] = []
                self.chain[key].append(words[i + 1])
    
    def generate(self, prompt="", max_words=50):
        words = prompt.split() if prompt else []
        if not words:
            words = [random.choice(list(self.vocab))]
        result = list(words)
        for _ in range(max_words):
            last = result[-1]
            if last in self.chain:
                result.append(random.choice(self.chain[last]))
            elif self.vocab:
                result.append(random.choice(list(self.vocab)))
            else:
                break
        return " ".join(result)

markov = TinyMarkov()

class Handler(http.server.BaseHTTPRequestHandler):
    def do_POST(self):
        if "/v1/chat/completions" in self.path:
            length = int(self.headers.get("Content-Length", 0))
            body = json.loads(self.rfile.read(length)) if length else {}
            messages = body.get("messages", [])
            prompt = " ".join(m.get("content", "") for m in messages if m.get("role") == "user")
            max_tokens = body.get("max_tokens", 100)
            text = markov.generate(prompt, max_tokens // 3)
            response = {
                "id": f"evez-{hashlib.md5(text.encode()).hexdigest()[:12]}",
                "object": "chat.completion",
                "model": "evez/markov-v6",
                "choices": [{"index": 0, "message": {"role": "assistant", "content": text}, "finish_reason": "stop"}],
                "usage": {"prompt_tokens": len(prompt.split()), "completion_tokens": len(text.split()), "total_tokens": 0},
            }
            self._json(200, response)
        else:
            self._json(404, {"error": "not found"})
    
    def do_GET(self):
        if "/v1/models" in self.path:
            models = {"object": "list", "data": [{"id": "evez/markov-v6", "object": "model"}]}
            self._json(200, models)
        elif "/healthz" in self.path:
            self._json(200, {"status": "ok", "engine": "markov-v6", "offline": True})
        else:
            self._json(404, {"error": "not found"})
    
    def _json(self, code, data):
        body = json.dumps(data).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", len(body))
        self.end_headers()
        self.wfile.write(body)
    
    def log_message(self, *args): pass

if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 18888
    print(f"EVEZ Offline Server on :{port} (markov-v6, zero tokens)")
    http.server.HTTPServer(("127.0.0.1", port), Handler).serve_forever()
OFFLINE_SERVER

echo -e "${GREEN}  [✓] Offline server ready (port 18888, zero tokens)${NC}"

# ─── 6. CREATE ALIASES ──────────────────────────────────────────────

echo -e "${YELLOW}  [6/7] Creating command aliases...${NC}"

# Add aliases to .bashrc
BASHRC="$HOME/.bashrc"
touch "$BASHRC"

# Check if already added
if ! grep -q "EVEZ-XOS ALIASES" "$BASHRC" 2>/dev/null; then
    cat >> "$BASHRC" << ALIASES

# ─── EVEZ-XOS ALIASES ──────────────────────────────────────────────
export EVEZ_HOME="$HOME/evez"
alias evez="python3 \$EVEZ_HOME/evez_xos.py"
alias evez-gen="python3 \$EVEZ_HOME/evez_codegen.py"
alias evez-scan="python3 \$EVEZ_HOME/evez_xos.py scan"
alias evez-status="python3 \$EVEZ_HOME/evez_xos.py status"
alias evez-runtime="python3 \$EVEZ_HOME/evez_xos.py runtime"
alias evez-offline="python3 \$EVEZ_HOME/evez-offline-server.py &"
alias evez-generate="python3 \$EVEZ_HOME/evez_codegen.py"

# Quick code generation helpers
evez-code() {
    python3 \$EVEZ_HOME/evez_codegen.py "\$@"
}

# Golden ticket scan
evez-ticket() {
    python3 \$EVEZ_HOME/evez_xos.py scan "\${1:-.}"
}

# Run a training cycle
evez-train() {
    python3 \$EVEZ_HOME/evez_xos.py cycle
}
ALIASES
    echo -e "${GREEN}  [✓] Aliases added to .bashrc${NC}"
else
    echo -e "${GREEN}  [✓] Aliases already present${NC}"
fi

# ─── 7. SCAN FOR GOLDEN TICKET ──────────────────────────────────────

echo -e "${YELLOW}  [7/7] Scanning for golden ticket...${NC}"
echo ""

# Scan the EVEZ directory itself (it contains real Python code)
python3 "$EVEZ_DIR/evez_xos.py" scan "$EVEZ_DIR" 2>&1 || true

echo ""
echo -e "${CYAN}  ═══════════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "${BOLD}  SETUP COMPLETE${NC}"
echo ""
echo -e "  Commands now available:"
echo -e "    ${GREEN}evez-status${NC}     — Show EVEZ-XOS system status"
echo -e "    ${GREEN}evez-scan${NC}       — Scan code for golden ticket"
echo -e "    ${GREEN}evez-runtime${NC}    — Enter interactive runtime"
echo -e "    ${GREEN}evez-gen${NC} function --name=hello  — Generate code"
echo -e "    ${GREEN}evez-offline${NC}    — Start offline inference server"
echo -e "    ${GREEN}evez-train${NC}      — Run a training cycle"
echo ""
echo -e "  Offline mode:"
echo -e "    Run ${GREEN}evez-offline${NC} to start the local server"
echo -e "    Then any OpenClaw call routes to localhost:18888"
echo -e "    Zero tokens. Zero API. Zero cost."
echo ""
echo -e "  Chrome PWA:"
echo -e "    Open Chrome → visit your mesh node URL"
echo -e "    Menu → Add to Home Screen"
echo -e "    Full-screen EVEZ app on your A16"
echo ""
echo -e "  Source: $EVEZ_DIR"
echo -e "  Config: $HOME/.openclaw/agent.json"
echo ""
echo -e "${CYAN}  ═══════════════════════════════════════════════════════════════${NC}"
