from __future__ import annotations

from collections import deque
from pathlib import Path
import json
from typing import Any

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import HTMLResponse

BASE_DIR = Path(__file__).resolve().parents[1]
HTML_PATH = BASE_DIR / "tools" / "hermetic_engine.html"
AUDIT_LOG_PATH = BASE_DIR / "src" / "memory" / "audit.jsonl"

app = FastAPI()


SENSITIVE_KEYS = {"signature", "api_key", "secret", "token", "password"}


def _sanitize(value: Any) -> Any:
    if isinstance(value, dict):
        sanitized = {}
        for key, val in value.items():
            if key.lower() in SENSITIVE_KEYS:
                continue
            sanitized[key] = _sanitize(val)
        return sanitized
    if isinstance(value, list):
        return [_sanitize(item) for item in value]
    return value


def _load_tail(n: int) -> list[dict[str, Any]]:
    if n <= 0:
        return []
    if not AUDIT_LOG_PATH.exists():
        return []
    entries: deque[dict[str, Any]] = deque(maxlen=n)
    with AUDIT_LOG_PATH.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            try:
                payload = json.loads(line)
            except json.JSONDecodeError:
                continue
            entries.append(_sanitize(payload))
    return list(entries)


@app.get("/", response_class=HTMLResponse)
def index() -> HTMLResponse:
    if not HTML_PATH.exists():
        raise HTTPException(status_code=404, detail="hermetic_engine.html not found")
    return HTMLResponse(HTML_PATH.read_text(encoding="utf-8"))


@app.get("/audit-tail")
def audit_tail(n: int = Query(200, ge=1, le=1000)) -> dict[str, Any]:
    return {"count": n, "entries": _load_tail(n)}
