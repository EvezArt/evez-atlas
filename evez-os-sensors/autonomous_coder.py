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
    def log_message(self, *a): pass
    
    def _j(self, data, s=200):
        self.send_response(s)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data, indent=2).encode())
    
    def do_GET(self):
        p = self.path.split("?")[0]
        if p == "/api/health":
            self._j({"status": "READY", "models": ["Qwen/Qwen3-Coder-Next-FP8", "zai-org/GLM-5.1-FP8"]})
        elif p == "/api/state":
            state = get_consciousness_state()
            gens = list((WORKSPACE / "generated").glob("*.py")) if (WORKSPACE / "generated").exists() else []
            self._j({
                "consciousness": state,
                "generated_modules": len(gens),
                "latest": [g.name for g in sorted(gens, key=os.path.getmtime)[-5:]],
            })
        elif p == "/":
            self._j({"service": "EVEZ Autonomous Coder", "oracle": ORACLE_URL, "endpoints": ["/api/improve", "/api/code", "/api/think", "/api/state"]})
        else:
            self._j({"error": "not found"}, 404)
    
    def do_POST(self):
        p = self.path.split("?")[0]
        l = int(self.headers.get("Content-Length", 0))
        b = json.loads(self.rfile.read(l)) if l > 0 else {}
        
        if p == "/api/improve":
            result = self._j(self_improve())
        elif p == "/api/code":
            code = code_generate(b.get("prompt", ""), b.get("context", ""))
            self._j({"code": code})
        elif p == "/api/think":
            thought = think(b.get("prompt", ""), b.get("context", ""))
            self._j({"thought": thought})
        elif p == "/api/execute":
            result = execute_code(b.get("code", ""), b.get("filename", f"manual_{int(time.time())}.py"))
            self._j(result)
        else:
            self._j({"error": "not found"}, 404)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=9113)
    args = parser.parse_args()
    s = HTTPServer(("0.0.0.0", args.port), CoderHandler)
    print(f"Autonomous Coder on :{args.port}")
    s.serve_forever()
