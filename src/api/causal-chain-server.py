from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import time
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


def _invalid_token(detail: str) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=detail,
        headers={"WWW-Authenticate": "Bearer"},
    )


def _get_jwt_secret() -> bytes:
    raw_secret = os.getenv("CAUSAL_CHAIN_JWT_SECRET")
    if not raw_secret:
        raise RuntimeError("CAUSAL_CHAIN_JWT_SECRET must be configured")
    return raw_secret.encode("utf-8")


def _audience_matches(audience_claim: Any, expected_audience: str) -> bool:
    if isinstance(audience_claim, str):
        return audience_claim == expected_audience
    if isinstance(audience_claim, list):
        return expected_audience in audience_claim
    return False


def _decode_jwt_payload(token: str) -> Dict[str, Any]:
    parts = token.split(".")
    if len(parts) != 3:
        raise _invalid_token("Invalid token format")

    try:
        header_bytes = _decode_base64url(parts[0])
        payload_bytes = _decode_base64url(parts[1])
        signature = _decode_base64url(parts[2])
        header = json.loads(header_bytes.decode("utf-8"))
        payload = json.loads(payload_bytes.decode("utf-8"))
    except (ValueError, json.JSONDecodeError):
        raise _invalid_token("Invalid token encoding")

    if not isinstance(header, dict) or header.get("alg") != "HS256":
        raise _invalid_token("Invalid token header")

    signing_input = f"{parts[0]}.{parts[1]}".encode("utf-8")
    expected_signature = hmac.new(_get_jwt_secret(), signing_input, hashlib.sha256).digest()
    if not hmac.compare_digest(signature, expected_signature):
        raise _invalid_token("Invalid token signature")

    if not isinstance(payload, dict):
        raise _invalid_token("Invalid token payload")

    now = int(time.time())
    exp = payload.get("exp")
    if not isinstance(exp, int) or exp <= now:
        raise _invalid_token("Token expired")

    expected_issuer = os.getenv("CAUSAL_CHAIN_JWT_ISSUER", "causal-chain-auth")
    if payload.get("iss") != expected_issuer:
        raise _invalid_token("Invalid token issuer")

    expected_audience = os.getenv("CAUSAL_CHAIN_JWT_AUDIENCE", "causal-chain-api")
    if not _audience_matches(payload.get("aud"), expected_audience):
        raise _invalid_token("Invalid token audience")

    return payload


def get_current_entity(request: Request) -> AuthContext:
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        raise _invalid_token("Missing Authorization header")

    scheme, _, token = auth_header.partition(" ")
    if scheme.lower() != "bearer" or not token:
        raise _invalid_token("Invalid Authorization header")

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
