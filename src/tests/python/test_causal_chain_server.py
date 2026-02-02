import importlib.util
import json
import os
from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient


def load_server_module():
    module_path = Path(__file__).resolve().parents[2] / "api" / "causal-chain-server.py"
    spec = importlib.util.spec_from_file_location("causal_chain_server", module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def setup_module(module):
    module._original_env = {
        "SECRET_KEY": os.environ.get("SECRET_KEY"),
        "API_KEY_SALT": os.environ.get("API_KEY_SALT"),
        "TRUST_FORWARDED_IPS": os.environ.get("TRUST_FORWARDED_IPS"),
    }
    os.environ["SECRET_KEY"] = "test-secret"
    os.environ["API_KEY_SALT"] = "test-salt"
    os.environ["TRUST_FORWARDED_IPS"] = "true"


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


def test_remote_request_blocked():
    client, _server = get_client()
    response = client.get(
        "/legion-status",
        headers={"X-API-Key": "tier1_builder", "X-Forwarded-For": "203.0.113.8"},
    )
    assert response.status_code == 403

    response = client.get(
        "/legion-status",
        headers={"X-API-Key": "tier1_builder", "X-Forwarded-For": "127.0.0.1"},
    )
    assert response.status_code == 200


def teardown_module(module):
    for key, value in module._original_env.items():
        if value is None:
            os.environ.pop(key, None)
        else:
            os.environ[key] = value


def test_audit_logging(tmp_path):
    client, server = get_client()
    audit_path = tmp_path / "audit.jsonl"
    audit_path.write_text("")

    with patch.object(server, "AUDIT_LOG_PATH", audit_path):
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
    assert first_entry["api_key_fingerprint"] != "unset"
    assert "source_ip" in first_entry


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


def test_navigation_ui_requires_tier2():
    client, _server = get_client()
    response = client.get(
        "/navigation-ui/data",
        headers={"X-API-Key": "tier1_builder"},
    )
    assert response.status_code == 403
