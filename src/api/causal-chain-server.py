from pathlib import Path
import hashlib
import hmac
import json
import os
import time

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, Header, HTTPException, Request
from pydantic import BaseModel
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

load_dotenv()

BASE_DIR = Path(__file__).resolve().parents[2]
MANIFEST_PATH = BASE_DIR / ".roo" / "archonic-manifest.json"
AUDIT_LOG_PATH = BASE_DIR / "src" / "memory" / "audit.jsonl"


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
@limiter.limit(_rate_limit_for_key)
def legion_status(request: Request, tier: int = Depends(verify_api_key)):
    entities = []
    for output_id, entity in ENTITY_REGISTRY.items():
        redacted = _redact_entity(entity, tier)
        entities.append({"output_id": output_id, **redacted})
    result = {"count": len(entities), "entities": entities}
    audit_log("legion", "/legion-status", tier, result, request.state.api_key)
    return result
