"""Tests for health and service status endpoints."""
import importlib.util
import os
from pathlib import Path

from fastapi.testclient import TestClient


def load_causal_server_module():
    module_path = Path(__file__).resolve().parents[2] / "api" / "causal-chain-server.py"
    spec = importlib.util.spec_from_file_location("causal_chain_server", module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_monitor_server_module():
    module_path = Path(__file__).resolve().parents[3] / "tools" / "monitor_server.py"
    spec = importlib.util.spec_from_file_location("monitor_server", module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def setup_module(module):
    os.environ["SECRET_KEY"] = "test-secret"


def test_causal_chain_root_endpoint():
    """Test the root endpoint returns API information."""
    server = load_causal_server_module()
    client = TestClient(server.app)
    
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    
    assert data["service"] == "Causal Chain API"
    assert data["status"] == "online"
    assert "endpoints" in data
    assert "authentication" in data


def test_causal_chain_health_endpoint():
    """Test the health check endpoint."""
    server = load_causal_server_module()
    client = TestClient(server.app)
    
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    
    assert data["status"] == "healthy"
    assert data["service"] == "causal-chain-api"
    assert "timestamp" in data
    assert "components" in data
    assert "entity_registry" in data["components"]
    assert data["components"]["entity_registry"] == 2  # Two entities in registry


def test_causal_chain_services_status():
    """Test the services status endpoint."""
    server = load_causal_server_module()
    client = TestClient(server.app)
    
    response = client.get("/services/status")
    assert response.status_code == 200
    data = response.json()
    
    assert "timestamp" in data
    assert "services" in data
    assert "communicative" in data
    assert "causal_chain_api" in data["services"]
    assert data["services"]["causal_chain_api"]["status"] == "online"


def test_monitor_server_health_endpoint():
    """Test the monitor server health check endpoint."""
    server = load_monitor_server_module()
    client = TestClient(server.app)
    
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    
    assert data["status"] == "healthy"
    assert data["service"] == "monitor-server"
    assert "timestamp" in data
    assert "components" in data
    assert "endpoints" in data


def test_monitor_server_api_info():
    """Test the monitor server API info endpoint."""
    server = load_monitor_server_module()
    client = TestClient(server.app)
    
    response = client.get("/api")
    assert response.status_code == 200
    data = response.json()
    
    assert data["service"] == "Monitor Server"
    assert data["status"] == "online"
    assert "endpoints" in data


def test_monitor_server_services_status():
    """Test the monitor server services status endpoint."""
    server = load_monitor_server_module()
    client = TestClient(server.app)
    
    response = client.get("/services/status")
    assert response.status_code == 200
    data = response.json()
    
    assert "timestamp" in data
    assert "services" in data
    assert "communicative" in data
    assert "monitor_server" in data["services"]
    assert data["services"]["monitor_server"]["status"] == "online"
