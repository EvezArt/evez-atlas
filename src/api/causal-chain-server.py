import hashlib
import hmac
import json
import os
import time
from pathlib import Path
from typing import Any, Dict

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
    AUDIT_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    entry = {
        "timestamp": time.time(),
        "entity_id": entity_id,
        "endpoint": endpoint,
        "tier": tier,
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
    return result
