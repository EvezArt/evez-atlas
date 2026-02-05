import base64
import hashlib
import hmac
import importlib.util
import json
import os
import sys
import time
from pathlib import Path

from fastapi.testclient import TestClient


os.environ.setdefault("CAUSAL_CHAIN_JWT_SECRET", "test-secret")
os.environ.setdefault("CAUSAL_CHAIN_JWT_ISSUER", "causal-chain-auth")
os.environ.setdefault("CAUSAL_CHAIN_JWT_AUDIENCE", "causal-chain-api")


def _load_app():
    module_path = Path(__file__).resolve().parents[2] / "api" / "causal-chain-server.py"
    spec = importlib.util.spec_from_file_location("causal_chain_server", module_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module.app


def _encode_segment(data: dict) -> str:
    raw = json.dumps(data, separators=(",", ":")).encode("utf-8")
    encoded = base64.urlsafe_b64encode(raw).decode("utf-8").rstrip("=")
    return encoded


def _sign_token(header_segment: str, payload_segment: str, secret: str = "test-secret") -> str:
    signing_input = f"{header_segment}.{payload_segment}".encode("utf-8")
    signature = hmac.new(secret.encode("utf-8"), signing_input, hashlib.sha256).digest()
    signature_segment = base64.urlsafe_b64encode(signature).decode("utf-8").rstrip("=")
    return f"{header_segment}.{payload_segment}.{signature_segment}"


def _make_token(tier: str, exp_offset_seconds: int = 300) -> str:
    header = _encode_segment({"alg": "HS256", "typ": "JWT"})
    payload = _encode_segment(
        {
            "tier": tier,
            "iss": "causal-chain-auth",
            "aud": "causal-chain-api",
            "exp": int(time.time()) + exp_offset_seconds,
        }
    )
    return _sign_token(header, payload)


def test_missing_token_is_unauthorized():
    client = TestClient(_load_app())
    response = client.post("/resolve-awareness")
    assert response.status_code == 401


def test_invalid_token_is_unauthorized():
    client = TestClient(_load_app())
    response = client.post(
        "/resolve-awareness",
        headers={"Authorization": "Bearer not-a-jwt"},
    )
    assert response.status_code == 401


def test_unsigned_token_is_unauthorized():
    client = TestClient(_load_app())
    header = _encode_segment({"alg": "none", "typ": "JWT"})
    payload = _encode_segment({"tier": "archonic"})
    response = client.post(
        "/resolve-awareness",
        headers={"Authorization": f"Bearer {header}.{payload}."},
    )
    assert response.status_code == 401


def test_standard_tier_can_resolve_awareness():
    client = TestClient(_load_app())
    response = client.post(
        "/resolve-awareness",
        headers={"Authorization": f"Bearer {_make_token('standard')}"},
    )
    assert response.status_code == 200
    assert response.json()["tier"] == "standard"


def test_standard_tier_cannot_access_legion_status():
    client = TestClient(_load_app())
    response = client.get(
        "/legion-status",
        headers={"Authorization": f"Bearer {_make_token('standard')}"},
    )
    assert response.status_code == 403


def test_elevated_tier_can_access_legion_status():
    client = TestClient(_load_app())
    response = client.get(
        "/legion-status",
        headers={"Authorization": f"Bearer {_make_token('elevated')}"},
    )
    assert response.status_code == 200
    assert response.json()["tier"] == "elevated"


def test_elevated_tier_cannot_access_stream_deity_awareness():
    client = TestClient(_load_app())
    response = client.get(
        "/stream-deity-awareness",
        headers={"Authorization": f"Bearer {_make_token('elevated')}"},
    )
    assert response.status_code == 403


def test_archonic_tier_can_access_stream_deity_awareness():
    client = TestClient(_load_app())
    response = client.get(
        "/stream-deity-awareness",
        headers={"Authorization": f"Bearer {_make_token('archonic')}"},
    )
    assert response.status_code == 200
    assert response.json()["tier"] == "archonic"


def test_expired_token_is_unauthorized():
    client = TestClient(_load_app())
    response = client.post(
        "/resolve-awareness",
        headers={"Authorization": f"Bearer {_make_token('standard', exp_offset_seconds=-1)}"},
    )
    assert response.status_code == 401
