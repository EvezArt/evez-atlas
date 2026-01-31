"""Simple read-only monitor server for Hermetic Engine audit logs."""

from __future__ import annotations

import json
from collections import deque
from pathlib import Path
from typing import Any, Deque, Iterable

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import HTMLResponse, JSONResponse

BASE_DIR = Path(__file__).resolve().parent
HTML_PATH = BASE_DIR / "hermetic_engine.html"
AUDIT_PATH = BASE_DIR.parent / "src" / "memory" / "audit.jsonl"

MAX_TAIL = 1000

app = FastAPI(title="Hermetic Engine Monitor", docs_url=None, redoc_url=None)

SENSITIVE_KEYS = {
    "api_key",
    "apikey",
    "authorization",
    "auth",
    "token",
    "access_token",
    "refresh_token",
    "password",
    "secret",
    "private_key",
}


def _redact_value(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: _redact_key_value(key, val) for key, val in value.items()}
    if isinstance(value, list):
        return [_redact_value(item) for item in value]
    return value


def _redact_key_value(key: str, value: Any) -> Any:
    if key.lower() in SENSITIVE_KEYS:
        return "[REDACTED]"
    return _redact_value(value)


def _iter_tail_lines(path: Path, limit: int) -> Deque[str]:
    tail: Deque[str] = deque(maxlen=limit)
    if not path.exists():
        return tail
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            stripped = line.strip()
            if stripped:
                tail.append(stripped)
    return tail


def _parse_lines(lines: Iterable[str]) -> list[dict[str, Any]]:
    parsed: list[dict[str, Any]] = []
    for line in lines:
        try:
            payload = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(payload, dict):
            parsed.append(_redact_value(payload))
        else:
            parsed.append({"value": _redact_value(payload)})
    return parsed


@app.get("/", response_class=HTMLResponse)
async def index() -> HTMLResponse:
    if not HTML_PATH.exists():
        raise HTTPException(status_code=404, detail="Hermetic Engine UI not found")
    return HTMLResponse(HTML_PATH.read_text(encoding="utf-8"))


@app.get("/audit-tail")
async def audit_tail(n: int = Query(200, ge=1, le=MAX_TAIL)) -> JSONResponse:
    lines = _iter_tail_lines(AUDIT_PATH, n)
    parsed = _parse_lines(lines)
    return JSONResponse({"count": len(parsed), "items": parsed})


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("tools.monitor_server:app", host="0.0.0.0", port=8000, reload=False)
