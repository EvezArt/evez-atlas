from pathlib import Path
import asyncio
import hashlib
import hmac
import json
import os
import time
from collections import deque
from contextlib import asynccontextmanager
from threading import Lock

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

# Audit log batching for better I/O performance
AUDIT_BUFFER = deque()
AUDIT_LOCK = Lock()
AUDIT_BATCH_SIZE = 10


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


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events."""
    # Startup: Nothing to do
    yield
    # Shutdown: Flush audit buffer
    _flush_audit_buffer()


limiter = Limiter(key_func=_rate_limit_key)
app = FastAPI(lifespan=lifespan)
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


def _flush_audit_buffer() -> None:
    """Flush the audit buffer to disk. Must be called without holding AUDIT_LOCK."""
    entries_to_write = []
    with AUDIT_LOCK:
        if not AUDIT_BUFFER:
            return
        # Move all entries out of buffer while holding lock
        while AUDIT_BUFFER:
            entries_to_write.append(AUDIT_BUFFER.popleft())
    
    # Write to disk without holding lock
    AUDIT_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with AUDIT_LOG_PATH.open("a", encoding="utf-8") as handle:
        for entry in entries_to_write:
            handle.write(json.dumps(entry) + "\n")


def audit_log(
    entity_id: str, endpoint: str, tier: int, result: dict, api_key: str
) -> None:
    """
    Add an audit log entry to the buffer for batched writing.
    
    Entries are buffered and written in batches for better I/O performance.
    """
    entry = {
        "timestamp": time.time(),
        "entity_id": entity_id,
        "endpoint": endpoint,
        "tier": tier,
        "api_key": api_key,
        "result": result,
    }
    should_flush = False
    with AUDIT_LOCK:
        AUDIT_BUFFER.append(entry)
        # Check if buffer is full
        if len(AUDIT_BUFFER) >= AUDIT_BATCH_SIZE:
            should_flush = True
    
    # Flush outside the lock to avoid reentrant lock issues
    if should_flush:
        _flush_audit_buffer()


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
    # Use list comprehension for better performance
    entities = [
        {"output_id": output_id, **_redact_entity(entity, tier)}
        for output_id, entity in ENTITY_REGISTRY.items()
    ]
    result = {"count": len(entities), "entities": entities}
    audit_log("legion", "/legion-status", tier, result, request.state.api_key)
    return result
