from pathlib import Path
import hashlib
import hmac
import html
import json
import os
import time
from pathlib import Path
from typing import Any, Dict

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, Header, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

load_dotenv()

BASE_DIR = Path(__file__).resolve().parents[2]
MANIFEST_PATH = BASE_DIR / ".roo" / "archonic-manifest.json"
AUDIT_LOG_PATH = BASE_DIR / "src" / "memory" / "audit.jsonl"


class ResolveRequest(BaseModel):
    output_id: str


app = FastAPI()


def load_manifest() -> Dict[str, Any]:
    if not MANIFEST_PATH.exists():
        return {"entities": [], "api_keys": {}}
    with MANIFEST_PATH.open("r", encoding="utf-8") as handle:
        return json.load(handle)


manifest = load_manifest()
TIER_MAP = {key: value["tier"] for key, value in manifest.get("api_keys", {}).items()}


limiter = Limiter(key_func=lambda request: request.headers.get("X-API-Key") or get_remote_address(request))
class ResolveAwarenessRequest(BaseModel):
    output_id: str


ENTITY_REGISTRY = {
    "output-001": {
        "status": "stable",
        "builder": "omega-lab",
        "trace": ["node-a", "node-b", "node-c"],
        "metadata": {"region": "orion", "epoch": "v1"},
    },
    "output-002": {
        "status": "degraded",
        "builder": "delta-works",
        "trace": ["node-x", "node-y"],
        "metadata": {"region": "centauri", "epoch": "v2"},
    },
}


def load_tier_map() -> dict:
    if not MANIFEST_PATH.exists():
        return {}
    with MANIFEST_PATH.open("r", encoding="utf-8") as handle:
        manifest = json.load(handle)
    api_keys = manifest.get("api_keys", {})
    return {key: int(value.get("tier", 0)) for key, value in api_keys.items()}


TIER_MAP = load_tier_map()


def _rate_limit_key(request: Request) -> str:
    return request.headers.get("X-API-Key") or get_remote_address(request)


limiter = Limiter(key_func=_rate_limit_key)
app = FastAPI()
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


def verify_api_key(x_api_key: str = Header(...)) -> int:
    if x_api_key not in TIER_MAP:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return TIER_MAP[x_api_key]


def rate_limit_by_tier(key: str) -> str:
    tier = TIER_MAP.get(key, 0)
    if tier == 0:
        return "10/minute"
    if tier == 3:
        return "100/minute"
    return "50/minute"


def audit_log(entity_id: str, endpoint: str, tier: int, result: Dict[str, Any]) -> None:
def verify_api_key(
    request: Request,
    x_api_key: str = Header(..., alias="X-API-Key"),
) -> int:
    tier = TIER_MAP.get(x_api_key)
    if tier is None:
        raise HTTPException(status_code=401, detail="Invalid API key")
    request.state.api_key = x_api_key
    request.state.tier = tier
    return tier


def audit_log(
    entity_id: str, endpoint: str, tier: int, result: dict, api_key: str
) -> None:
    AUDIT_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    entry = {
        "timestamp": time.time(),
        "entity_id": entity_id,
        "endpoint": endpoint,
        "tier": tier,
        "api_key": api_key,
        "result": result,
    }
    with AUDIT_LOG_PATH.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(entry) + "\n")


def hmac_sign(data: Dict[str, Any]) -> str:
    secret = os.getenv("SECRET_KEY")
    if not secret:
        raise HTTPException(status_code=500, detail="SECRET_KEY is not configured")
    serialized = json.dumps(data, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hmac.new(secret.encode("utf-8"), serialized, hashlib.sha256).hexdigest()


def redact_by_tier(data: Dict[str, Any], tier: int) -> Dict[str, Any]:
    redacted = {
        "output_id": data["output_id"],
        "status": data["status"],
    }
    if tier >= 1:
        redacted["builder_entity"] = data["builder_entity"]
    if tier >= 2:
        redacted["server_trace"] = data["server_trace"]
    if tier >= 3:
        redacted["metadata"] = data["metadata"]
    return redacted


@app.post("/resolve-awareness")
@limiter.limit(rate_limit_by_tier)
async def resolve_awareness(
    request: Request,
    payload: ResolveRequest,
    tier: int = Depends(verify_api_key),
) -> Dict[str, Any]:
    record = {
        "output_id": payload.output_id,
        "status": "active",
        "builder_entity": "omega",
        "server_trace": ["node-a", "node-b"],
        "metadata": {"priority": "high", "signal": "stable"},
    }
    redacted = redact_by_tier(record, tier)
    signature = hmac_sign(redacted)
    response = {**redacted, "signature": signature}
    audit_log(payload.output_id, "/resolve-awareness", tier, {"response_keys": list(response.keys())})
def hmac_sign(data: dict) -> str:
    secret = os.getenv("SECRET_KEY", "")
    if not secret:
        raise HTTPException(status_code=500, detail="Missing SECRET_KEY")
    payload = json.dumps(data, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hmac.new(secret.encode("utf-8"), payload, hashlib.sha256).hexdigest()


def _rate_limit_for_key(key: str) -> str:
    tier = TIER_MAP.get(key, 0)
    if tier <= 0:
        return "10/minute"
    if tier >= 3:
        return "100/minute"
    return "50/minute"


def _redact_entity(entity: dict, tier: int) -> dict:
    payload = {"status": entity.get("status")}
    if tier >= 1:
        payload["builder"] = entity.get("builder")
    if tier >= 2:
        payload["trace"] = entity.get("trace")
    if tier >= 3:
        payload["metadata"] = entity.get("metadata")
    return payload


def _format_vector(vector: list, precision: int = 3) -> str:
    return "[" + ", ".join(f"{value:.{precision}f}" for value in vector) + "]"


@app.post("/resolve-awareness")
@limiter.limit(_rate_limit_for_key)
def resolve_awareness(
    request: Request,
    payload: ResolveAwarenessRequest,
    tier: int = Depends(verify_api_key),
):
    entity = ENTITY_REGISTRY.get(payload.output_id)
    if entity is None:
        raise HTTPException(status_code=404, detail="Entity not found")
    redacted = _redact_entity(entity, tier)
    response = {"output_id": payload.output_id, **redacted}
    response["signature"] = hmac_sign(response)
    audit_log(
        payload.output_id,
        "/resolve-awareness",
        tier,
        response,
        request.state.api_key,
    )
    return response


@app.get("/legion-status")
@limiter.limit(rate_limit_by_tier)
async def legion_status(request: Request, tier: int = Depends(verify_api_key)) -> Dict[str, Any]:
    entities = []
    for entity in manifest.get("entities", []):
        base = {
            "output_id": entity["entity_id"],
            "status": entity["status"],
        }
        if tier >= 1:
            base["builder_entity"] = entity["builder_entity"]
        if tier >= 2:
            base["server_trace"] = entity["server_trace"]
        if tier >= 3:
            base["metadata"] = entity["metadata"]
        entities.append(base)
    result = {"count": len(entities), "entities": entities}
    audit_log("legion", "/legion-status", tier, {"count": len(entities)})
@limiter.limit(_rate_limit_for_key)
def legion_status(request: Request, tier: int = Depends(verify_api_key)):
    entities = []
    for output_id, entity in ENTITY_REGISTRY.items():
        redacted = _redact_entity(entity, tier)
        entities.append({"output_id": output_id, **redacted})
    result = {"count": len(entities), "entities": entities}
    audit_log("legion", "/legion-status", tier, result, request.state.api_key)
    return result


@app.get("/navigation-ui", response_class=HTMLResponse)
@limiter.limit(_rate_limit_for_key)
def navigation_ui(request: Request, tier: int = Depends(verify_api_key)):
    from demo import build_navigation_ui_state

    state = build_navigation_ui_state()
    evaluation = state["evaluation"]
    candidate_rows = []
    for idx, candidate in enumerate(state["candidates"]):
        probability = evaluation["candidate_probabilities"][idx]
        rank = evaluation["ranked_candidates"].index(idx) + 1
        candidate_rows.append(
            (
                idx,
                _format_vector(candidate),
                f"{probability:.3f}",
                rank,
            )
        )
    projection_rows = [
        (idx, f"{value:.3f}") for idx, value in enumerate(evaluation["manifold_projection"])
    ]
    recursive_rows = []
    for idx, step in enumerate(state["recursive"], start=1):
        recursive_rows.append(
            (
                idx,
                step["top_candidate"],
                f"{step['top_probability']:.3f}",
                f"{step['entropy']:.3f}",
                f"{step['projection_entropy']:.3f}",
            )
        )
    state_snapshot = html.escape(
        json.dumps(state, indent=2, sort_keys=True)
    )
    html_parts = [
        "<!DOCTYPE html>",
        "<html lang='en'>",
        "<head>",
        "<meta charset='UTF-8' />",
        "<meta name='viewport' content='width=device-width, initial-scale=1' />",
        "<title>Quantum Navigation Interface</title>",
        "<style>",
        "body { font-family: 'Inter', sans-serif; margin: 32px; color: #101418; }",
        "h1, h2 { color: #1e2a3a; }",
        "table { border-collapse: collapse; width: 100%; margin-bottom: 24px; }",
        "th, td { border: 1px solid #d7dde5; padding: 8px 12px; text-align: left; }",
        "th { background: #f2f5f9; }",
        ".card { padding: 16px; border-radius: 12px; background: #f8fafc; margin-bottom: 20px; }",
        "</style>",
        "</head>",
        "<body>",
        "<h1>Quantum Navigation Interface</h1>",
        "<div class='card'>",
        "<p>Outerfacing sensory navigation snapshot derived from the latest sequence evaluation.</p>",
        "</div>",
        "<h2>Environmental Sensory Tasks</h2>",
        "<table>",
        "<thead><tr><th>Task</th><th>Vector</th></tr></thead>",
        "<tbody>",
    ]
    for task in state["sensor_tasks"]:
        html_parts.append(
            "<tr><td>"
            + html.escape(task["name"])
            + "</td><td>"
            + html.escape(_format_vector(task["vector"]))
            + "</td></tr>"
        )
    html_parts.extend(
        [
            "</tbody>",
            "</table>",
            "<h2>Sequence Embedding</h2>",
            "<div class='card'>",
            "<p><strong>Embedding:</strong> "
            + html.escape(_format_vector(evaluation["embedding"]))
            + "</p>",
            "<p><strong>Entropy:</strong> "
            + f"{evaluation['entropy']:.3f}"
            + "</p>",
            "<p><strong>Projection entropy:</strong> "
            + f"{evaluation['projection_entropy']:.3f}"
            + "</p>",
            "</div>",
            "<h2>Candidate Probabilities</h2>",
            "<table>",
            "<thead><tr><th>Candidate</th><th>Vector</th><th>Probability</th><th>Rank</th></tr></thead>",
            "<tbody>",
        ]
    )
    for idx, vector, probability, rank in candidate_rows:
        html_parts.append(
            "<tr><td>"
            + str(idx)
            + "</td><td>"
            + html.escape(vector)
            + "</td><td>"
            + probability
            + "</td><td>"
            + str(rank)
            + "</td></tr>"
        )
    html_parts.extend(
        [
            "</tbody>",
            "</table>",
            "<h2>Manifold Projection</h2>",
            "<table>",
            "<thead><tr><th>Anchor</th><th>Projection</th></tr></thead>",
            "<tbody>",
        ]
    )
    for idx, value in projection_rows:
        html_parts.append(
            "<tr><td>"
            + str(idx)
            + "</td><td>"
            + value
            + "</td></tr>"
        )
    html_parts.extend(
        [
            "</tbody>",
            "</table>",
        "<h2>Recursive Navigation Steps</h2>",
        "<table>",
        "<thead><tr><th>Step</th><th>Top Candidate</th><th>Top Probability</th>"
        "<th>Entropy</th><th>Projection Entropy</th></tr></thead>",
        "<tbody>",
        ]
    )
    for step, top_candidate, top_probability, entropy, projection_entropy in recursive_rows:
        html_parts.append(
            "<tr><td>"
            + str(step)
            + "</td><td>"
            + str(top_candidate)
            + "</td><td>"
            + top_probability
            + "</td><td>"
            + entropy
            + "</td><td>"
            + projection_entropy
            + "</td></tr>"
        )
    html_parts.extend(
        [
            "</tbody>",
            "</table>",
            "<h2>High-Definition State Snapshot</h2>",
            "<div class='card'>",
            "<pre>",
            state_snapshot,
            "</pre>",
            "</div>",
            "</body>",
            "</html>",
        ]
    )
    return HTMLResponse("".join(html_parts))


@app.get("/navigation-ui/data", response_class=JSONResponse)
@limiter.limit(_rate_limit_for_key)
def navigation_ui_data(request: Request, tier: int = Depends(verify_api_key)):
    from demo import build_navigation_ui_state

    state = build_navigation_ui_state()
    return JSONResponse(state)


# ========== Jubilee Integration ==========
# Add Jubilee router for debt forgiveness
try:
    from src.api.jubilee_endpoints import router as jubilee_router
    app.include_router(jubilee_router)
except ImportError:
    # Jubilee endpoints not available
    pass


# ========== WebSocket for Real-time Swarm Communication ==========
from fastapi import WebSocket, WebSocketDisconnect
from typing import Set

active_connections: Set[WebSocket] = set()


@app.websocket("/ws/swarm")
async def swarm_websocket(websocket: WebSocket):
    """
    WebSocket endpoint for real-time swarm communication.
    
    Entities can connect and broadcast messages to all other connected entities.
    """
    await websocket.accept()
    active_connections.add(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # Broadcast to all connected entities except sender
            for connection in active_connections:
                if connection != websocket:
                    await connection.send_text(data)
    except WebSocketDisconnect:
        active_connections.remove(websocket)
    except Exception:
        if websocket in active_connections:
            active_connections.remove(websocket)


# ========== Swarm Status Endpoint ==========
@app.get("/swarm-status")
def swarm_status():
    """Get current swarm status from the director."""
    try:
        from src.mastra.agents.swarm_director import director
        status = director.get_swarm_status()
        status["websocket_connections"] = len(active_connections)
        return status
    except Exception as e:
        return {
            "error": str(e),
            "websocket_connections": len(active_connections)
        }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
