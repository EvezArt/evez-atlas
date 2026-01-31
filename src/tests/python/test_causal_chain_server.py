import importlib.util
import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

MODULE_PATH = Path(__file__).resolve().parents[2] / "api" / "causal-chain-server.py"

spec = importlib.util.spec_from_file_location("causal_chain_server", MODULE_PATH)
module = importlib.util.module_from_spec(spec)
if spec.loader is None:
    raise RuntimeError("Unable to load causal-chain-server module")
spec.loader.exec_module(module)


@pytest.fixture(autouse=True)
def configure_env(monkeypatch):
    monkeypatch.setenv("SECRET_KEY", "test-secret")
    module.AUDIT_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    module.AUDIT_LOG_PATH.write_text("")


@pytest.fixture()
def client():
    return TestClient(module.app)


def test_tier0_redaction(client):
import os
from pathlib import Path

from fastapi.testclient import TestClient


def load_server_module():
    module_path = Path(__file__).resolve().parents[2] / "api" / "causal-chain-server.py"
    spec = importlib.util.spec_from_file_location("causal_chain_server", module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def setup_module(module):
    os.environ["SECRET_KEY"] = "test-secret"


def get_client():
    server = load_server_module()
    return TestClient(server.app), server


def test_tier0_redaction():
    client, _server = get_client()
    response = client.post(
        "/resolve-awareness",
        headers={"X-API-Key": "tier0_public"},
        json={"output_id": "output-001"},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "active"
    assert "builder_entity" not in payload
    assert "server_trace" not in payload
    assert "metadata" not in payload
    assert "signature" in payload


def test_tier3_full_access(client):
    assert payload["status"] == "stable"
    assert "builder" not in payload
    assert "trace" not in payload
    assert "metadata" not in payload


def test_tier3_full_access():
    client, _server = get_client()
    response = client.post(
        "/resolve-awareness",
        headers={"X-API-Key": "tier3_director"},
        json={"output_id": "output-001"},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["builder_entity"] == "omega"
    assert payload["server_trace"] == ["node-a", "node-b"]
    assert payload["metadata"]["priority"] == "high"
    assert "signature" in payload


def test_invalid_api_key(client):
    assert payload["status"] == "stable"
    assert payload["builder"] == "omega-lab"
    assert payload["trace"] == ["node-a", "node-b", "node-c"]
    assert payload["metadata"]["region"] == "orion"


def test_invalid_api_key():
    client, _server = get_client()
    response = client.post(
        "/resolve-awareness",
        headers={"X-API-Key": "invalid"},
        json={"output_id": "output-001"},
    )
    assert response.status_code == 401


def test_audit_logging(client):
    client.post(
        "/resolve-awareness",
        headers={"X-API-Key": "tier0_public"},
        json={"output_id": "output-002"},
    )
    entries = [
        json.loads(line)
        for line in module.AUDIT_LOG_PATH.read_text().splitlines()
        if line.strip()
    ]
    assert any(entry["endpoint"] == "/resolve-awareness" for entry in entries)


def test_hmac_signature(client):
    response = client.post(
        "/resolve-awareness",
        headers={"X-API-Key": "tier3_director"},
        json={"output_id": "output-003"},
    )
    payload = response.json()
    signature = payload.pop("signature")
    expected = module.hmac_sign(payload)
def test_audit_logging(tmp_path):
    client, server = get_client()
    audit_path = Path(server.AUDIT_LOG_PATH)
    audit_path.write_text("")

    response = client.post(
        "/resolve-awareness",
        headers={"X-API-Key": "tier1_builder"},
        json={"output_id": "output-001"},
    )
    assert response.status_code == 200

    response = client.get(
        "/legion-status",
        headers={"X-API-Key": "tier1_builder"},
    )
    assert response.status_code == 200

    lines = audit_path.read_text().strip().splitlines()
    assert len(lines) == 2
    first_entry = json.loads(lines[0])
    assert first_entry["endpoint"] == "/resolve-awareness"


def test_hmac_signature():
    client, server = get_client()
    response = client.post(
        "/resolve-awareness",
        headers={"X-API-Key": "tier2_admin"},
        json={"output_id": "output-002"},
    )
    assert response.status_code == 200
    payload = response.json()
    signature = payload.pop("signature")
    expected = server.hmac_sign(payload)
    assert signature == expected
