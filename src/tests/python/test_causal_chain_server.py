import base64
import importlib.util
import json
from pathlib import Path

from fastapi.testclient import TestClient


def _load_app():
    module_path = Path(__file__).resolve().parents[2] / "api" / "causal-chain-server.py"
    spec = importlib.util.spec_from_file_location("causal_chain_server", module_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module.app


def _encode_segment(data: dict) -> str:
    raw = json.dumps(data, separators=(",", ":")).encode("utf-8")
    encoded = base64.urlsafe_b64encode(raw).decode("utf-8").rstrip("=")
    return encoded


def _make_token(tier: str) -> str:
    header = _encode_segment({"alg": "none", "typ": "JWT"})
    payload = _encode_segment({"tier": tier})
    return f"{header}.{payload}."


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
