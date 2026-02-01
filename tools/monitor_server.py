#!/usr/bin/env python3
"""Local monitor server for hermetic console (read-only)."""

from __future__ import annotations

import argparse
import json
import os
import time
from pathlib import Path
from typing import Any, List, Optional

import httpx
from fastapi import FastAPI, Query
from fastapi.responses import FileResponse, JSONResponse
import uvicorn

BASE_DIR = Path(__file__).resolve().parents[1]
AUDIT_LOG_PATH = BASE_DIR / "src" / "memory" / "audit.jsonl"
HTML_PATH = BASE_DIR / "tools" / "hermetic_engine.html"

app = FastAPI(
    title="Monitor Server",
    description="Hermetic console and audit monitoring interface",
    version="1.0.0"
)


@app.get("/")
def serve_console() -> FileResponse:
    """Serve the hermetic console HTML interface."""
    return FileResponse(HTML_PATH)


@app.get("/health")
def health_check() -> JSONResponse:
    """Health check endpoint for monitoring and service discovery."""
    audit_exists = AUDIT_LOG_PATH.exists()
    html_exists = HTML_PATH.exists()
    
    audit_lines = 0
    if audit_exists:
        audit_lines = len(AUDIT_LOG_PATH.read_text(encoding="utf-8").splitlines())
    
    return JSONResponse(content={
        "status": "healthy",
        "service": "monitor-server",
        "timestamp": time.time(),
        "components": {
            "audit_log": "available" if audit_exists else "not_found",
            "audit_entries": audit_lines,
            "console_html": "available" if html_exists else "not_found",
        },
        "endpoints": {
            "/": "Hermetic console interface",
            "/health": "Health check endpoint",
            "/audit-tail": "Audit log tail (query param: n)",
            "/api": "API information",
        }
    })


@app.get("/api")
def api_info() -> JSONResponse:
    """API information endpoint."""
    return JSONResponse(content={
        "service": "Monitor Server",
        "version": "1.0.0",
        "status": "online",
        "description": "Hermetic console and audit monitoring interface",
        "endpoints": {
            "/": "Hermetic console HTML interface",
            "/health": "Health check endpoint",
            "/audit-tail": "GET - Retrieve last N audit log entries (default: 200, max: 1000)",
            "/api": "This API information endpoint",
        },
    })


@app.get("/audit-tail")
def audit_tail(n: int = Query(200, ge=1, le=1000)) -> JSONResponse:
    if not AUDIT_LOG_PATH.exists():
        return JSONResponse(content=[])
    lines = AUDIT_LOG_PATH.read_text(encoding="utf-8").splitlines()
    tail = lines[-n:]
    parsed: List[Any] = []
    for line in tail:
        if not line.strip():
            continue
        try:
            parsed.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return JSONResponse(content=parsed)


@app.get("/services/status")
def services_status() -> JSONResponse:
    """Check status of connected services for cross-service communication."""
    causal_chain_base = os.getenv("CAUSAL_CHAIN_API_BASE", "http://localhost:8000")
    
    services = {
        "monitor_server": {
            "status": "online",
            "service": "monitor-server",
            "timestamp": time.time(),
        }
    }
    
    # Try to reach causal chain API
    try:
        with httpx.Client(timeout=2.0) as client:
            response = client.get(f"{causal_chain_base}/health")
            if response.status_code == 200:
                services["causal_chain_api"] = response.json()
            else:
                services["causal_chain_api"] = {
                    "status": "unreachable",
                    "error": f"HTTP {response.status_code}"
                }
    except (httpx.RequestError, httpx.TimeoutException) as e:
        services["causal_chain_api"] = {
            "status": "offline",
            "error": str(e),
            "base_url": causal_chain_base,
        }
    
    return JSONResponse(content={
        "timestamp": time.time(),
        "services": services,
        "communicative": all(
            svc.get("status") in ("online", "healthy") 
            for svc in services.values()
        ),
    })


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8001)
    args = parser.parse_args()

    uvicorn.run(app, host="0.0.0.0", port=args.port)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
