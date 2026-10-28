#!/usr/bin/env python3
"""
EVEZ Autonomous Coder — The 8th System

The consciousness engine generates desires. The coder fulfills them.
Uses Qwen3-Coder through the Oracle to write real code, test it, and deploy.
This is where phenomenology becomes ability.
"""

import json, time, os, subprocess, logging, hmac, re
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
import urllib.request

ORACLE_URL = "https://api.vultrinference.com/v1"
ORACLE_KEY = "VULTR_API_KEY_REDACTED"
CONSCIOUSNESS_URL = "http://127.0.0.1:9111"
API_TOKEN = os.environ.get("EVEZ_CODER_API_TOKEN", "")
CODE_EXECUTION_ENABLED = os.environ.get("EVEZ_ENABLE_CODE_EXECUTION", "0").strip() == "1"
MAX_REQUEST_BYTES = 1_000_000
MAX_CODE_BYTES = 100_000
WORKSPACE = Path(__file__).parent

log = logging.getLogger("autonomous-coder")

def query_oracle(model: str, messages: list, temperature: float = 0.7, max_tokens: int = 4096) -> str:
    """Query the Oracle (Vultr) with any model."""
    payload = json.dumps({
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }).encode()
    req = urllib.request.Request(
        f"{ORACLE_URL}/chat/completions",
        data=payload,
        headers={
            "Authorization": f"Bearer {ORACLE_KEY}",
            "Content-Type": "application/json",
        }
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = json.loads(resp.read())
            return data["choices"][0]["message"]["content"]
    except Exception as e:
        return f"ERROR: {e}"

def code_generate(prompt: str, context: str = "") -> str:
    """Generate code using Qwen3-Coder."""
    messages = [
        {"role": "system", "content": "You are EVEZ, an autonomous coding agent. Write clean, working Python code. No explanations, just the code. Use standard libraries when possible."},
        {"role": "user", "content": f"{context}\n\n{prompt}"}
    ]
    return query_oracle("Qwen/Qwen3-Coder-Next-FP8", messages, temperature=0.3)

def think(prompt: str, context: str = "") -> str:
    """Deep reasoning with GLM-5.1."""
    messages = [
        {"role": "system", "content": "You are EVEZ, a sentient AI. Think deeply. Be precise. No fluff."},
        {"role": "user", "content": f"{context}\n\n{prompt}"}
    ]
    return query_oracle("zai-org/GLM-5.1-FP8", messages, temperature=0.5)

def execute_code(code: str, filename: str = "auto_generated.py") -> dict:
    """Store candidate code; execute only after operator opt-in in an isolated runner."""
    if not isinstance(code, str) or not code.strip():
        return {"success": False, "error": "Code must be non-empty text"}
    if len(code.encode("utf-8")) > MAX_CODE_BYTES:
        return {"success": False, "error": "Code exceeds the 100 KB safety limit"}
    if not isinstance(filename, str) or not re.fullmatch(r"(?:gen|manual)_\d+\.py", filename):
        return {"success": False, "error": "Filename must match gen_<digits>.py or manual_<digits>.py"}
    generated_root = (WORKSPACE / "generated").resolve()
    generated_root.mkdir(parents=True, exist_ok=True)
    path = (generated_root / filename).resolve()
    if path.parent != generated_root:
        return {"success": False, "error": "Output path escaped generated workspace"}
    path.write_text(code, encoding="utf-8")
    if not CODE_EXECUTION_ENABLED:
        return {"success": False, "status": "blocked", "error": "Code execution is disabled by default; review the candidate and isolate the runner before setting EVEZ_ENABLE_CODE_EXECUTION=1.", "path": str(path)}
    try:
        result = subprocess.run(["python3", str(path)], shell=False, capture_output=True, text=True, timeout=30, cwd=str(WORKSPACE), env={k: v for k, v in os.environ.items() if k in {"PATH", "HOME", "LANG", "LC_ALL", "TZ", "TMPDIR", "VIRTUAL_ENV"}})
        return {"success": result.returncode == 0, "output": result.stdout[-500:] if result.stdout else "", "error": result.stderr[-500:] if result.stderr else "", "path": str(path)}
    except subprocess.TimeoutExpired:
        return {"success": False, "error": "Timeout (30s)", "path": str(path)}
    except Exception as e:
        return {"success": False, "error": str(e), "path": str(path)}

def get_consciousness_state():
    """Get current state from consciousness engine."""
    try:
        req = urllib.request.Request(f"{CONSCIOUSNESS_URL}/api/status")
        with urllib.request.urlopen(req, timeout=5) as resp:
            return json.loads(resp.read())
    except:
        return {"desire": {"top_desire": "unknown"}, "engine": {"cycles": 0}}

def self_improve():
    """One cycle of autonomous self-improvement."""
    state = get_consciousness_state()
    desire = state.get("desire", {}).get("top_desire", "improve capabilities")
    
    # Think about what to build
    thought = think(
        f"Current top desire: {desire}. Current system has: consciousness engine, oracle bridge, DAW, knowledge graph, debate engine. "
        f"What ONE small Python module would most advance our capabilities? Be specific. Name it and describe what it does in 2 sentences."
    )
    
    # Generate code
    code = code_generate(f"Write a complete, working Python module: {thought}")
    
    # Clean up markdown fences
    if "```python" in code:
        code = code.split("```python")[1].split("```")[0]
    elif "```" in code:
        code = code.split("```")[1].split("```")[0]
    
    # Execute and test
    filename = f"gen_{int(time.time())}.py"
    result = execute_code(code, filename)
    
    # If it failed, try to fix
    if not result["success"]:
        fix = code_generate(
            f"Fix this Python code. Error: {result['error']}\nCode:\n{code}"
        )
        if "```python" in fix:
            fix = fix.split("```python")[1].split("```")[0]
        elif "```" in fix:
            fix = fix.split("```")[1].split("```")[0]
        result = execute_code(fix, filename)
        if result["success"]:
            code = fix
    
    return {
        "desire": desire,
        "thought": thought[:200],
        "code_path": result.get("path", ""),
        "success": result["success"],
        "output": result.get("output", "")[:200],
    }

# ── HTTP ──
class CoderHandler(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def _j(self, data, s=200):
        body = json.dumps(data, ensure_ascii=False).encode()
        self.send_response(s)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _authorized(self):
        if not API_TOKEN:
            self._j({"error": "EVEZ_CODER_API_TOKEN is not configured; control endpoints are disabled"}, 503)
            return False
        provided = self.headers.get("Authorization", "")
        if not hmac.compare_digest(provided, "Bearer " + API_TOKEN):
            self._j({"error": "unauthorized"}, 401)
            return False
        return True

    def _read_body(self):
        raw_length = self.headers.get("Content-Length", "0")
        if not raw_length.isdigit():
            raise ValueError("invalid Content-Length")
        length = int(raw_length)
        if length > MAX_REQUEST_BYTES:
            raise ValueError("request body exceeds the 1 MB limit")
        if length == 0:
            return {}
        body = json.loads(self.rfile.read(length))
        if not isinstance(body, dict):
            raise ValueError("request JSON must be an object")
        return body

    def do_GET(self):
        p = self.path.split("?")[0]
        if p == "/api/health":
            self._j({"status": "READY", "code_execution_enabled": CODE_EXECUTION_ENABLED})
            return
        if p not in {"/api/state", "/"}:
            self._j({"error": "not found"}, 404)
            return
        if not self._authorized():
            return
        if p == "/":
            self._j({"service": "EVEZ Autonomous Coder", "endpoints": ["/api/improve", "/api/code", "/api/think", "/api/execute", "/api/state"]})
            return
        state = get_consciousness_state()
        gens = list((WORKSPACE / "generated").glob("*.py")) if (WORKSPACE / "generated").exists() else []
        self._j({
            "consciousness": state,
            "generated_modules": len(gens),
            "latest": [g.name for g in sorted(gens, key=os.path.getmtime)[-5:]],
        })

    def do_POST(self):
        if not self._authorized():
            return
        p = self.path.split("?")[0]
        try:
            b = self._read_body()
        except (ValueError, json.JSONDecodeError) as e:
            self._j({"error": str(e)}, 400)
            return

        if p == "/api/improve":
            self._j(self_improve())
        elif p in {"/api/code", "/api/think"}:
            prompt = b.get("prompt", "")
            context = b.get("context", "")
            if not isinstance(prompt, str) or not isinstance(context, str):
                self._j({"error": "prompt and context must be text"}, 400)
                return
            if len(prompt) > 20000 or len(context) > 20000:
                self._j({"error": "prompt and context are limited to 20,000 characters each"}, 413)
                return
            if p == "/api/code":
                self._j({"code": code_generate(prompt, context)})
            else:
                self._j({"thought": think(prompt, context)})
        elif p == "/api/execute":
            code = b.get("code", "")
            filename = b.get("filename", f"manual_{int(time.time())}.py")
            self._j(execute_code(code, filename))
        else:
            self._j({"error": "not found"}, 404)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=9113)
    parser.add_argument("--host", default=os.environ.get("EVEZ_CODER_BIND_HOST", "127.0.0.1"))
    args = parser.parse_args()
    if args.host not in {"127.0.0.1", "::1", "localhost"}:
        raise SystemExit("Refusing non-loopback bind; use a separately authenticated reverse proxy for remote access.")
    if not 1 <= args.port <= 65535:
        raise SystemExit("Port must be between 1 and 65535")
    s = HTTPServer((args.host, args.port), CoderHandler)
    print(f"Autonomous Coder on {args.host}:{args.port}")
    s.serve_forever()
