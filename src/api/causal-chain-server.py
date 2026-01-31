from __future__ import annotations

import base64
import json
from dataclasses import dataclass
from typing import Any, Dict

from fastapi import Depends, FastAPI, HTTPException, Request, status


app = FastAPI()


@dataclass(frozen=True)
class AuthContext:
    tier: str
    claims: Dict[str, Any]


ACCESS_TIERS = {
    "standard": 1,
    "elevated": 2,
    "archonic": 3,
}


def _decode_base64url(value: str) -> bytes:
    padding_needed = (4 - len(value) % 4) % 4
    value += "=" * padding_needed
    return base64.urlsafe_b64decode(value.encode("utf-8"))


def _decode_jwt_payload(token: str) -> Dict[str, Any]:
    parts = token.split(".")
    if len(parts) != 3:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token format",
            headers={"WWW-Authenticate": "Bearer"},
        )
    try:
        payload_bytes = _decode_base64url(parts[1])
        payload = json.loads(payload_bytes.decode("utf-8"))
    except (ValueError, json.JSONDecodeError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not isinstance(payload, dict):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return payload


def get_current_entity(request: Request) -> AuthContext:
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing Authorization header",
            headers={"WWW-Authenticate": "Bearer"},
        )
    scheme, _, token = auth_header.partition(" ")
    if scheme.lower() != "bearer" or not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Authorization header",
            headers={"WWW-Authenticate": "Bearer"},
        )
    claims = _decode_jwt_payload(token)
    tier = claims.get("tier")
    if tier not in ACCESS_TIERS:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Unknown access tier",
        )
    return AuthContext(tier=tier, claims=claims)


def require_tier(minimum_tier: str):
    def _dependency(context: AuthContext = Depends(get_current_entity)) -> AuthContext:
        if ACCESS_TIERS[context.tier] < ACCESS_TIERS[minimum_tier]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient access tier",
            )
        return context

    return _dependency


@app.post("/resolve-awareness")
async def resolve_awareness(
    context: AuthContext = Depends(require_tier("standard")),
) -> Dict[str, Any]:
    return {"status": "resolved", "tier": context.tier}


@app.get("/legion-status")
async def legion_status(
    context: AuthContext = Depends(require_tier("elevated")),
) -> Dict[str, Any]:
    return {"status": "active", "tier": context.tier}


@app.get("/stream-deity-awareness")
async def stream_deity_awareness(
    context: AuthContext = Depends(require_tier("archonic")),
) -> Dict[str, Any]:
    return {"stream": "open", "tier": context.tier}
