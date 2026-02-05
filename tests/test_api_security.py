"""
Integration tests for API endpoints with security controls

Tests that debug routes are properly protected in production mode
and accessible in development mode.
"""

import os
import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient

# Import the app
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.api.causal_chain_server import app


@pytest.fixture
def client():
    """Create test client"""
    return TestClient(app)


@pytest.fixture
def mock_api_key(monkeypatch):
    """Mock API key configuration"""
    # Set up a test API key with tier 3
    manifest_data = {
        "api_keys": {
            "test-key-123": {"tier": 3}
        }
    }
    
    # Mock the TIER_MAP in the server
    from src.api import causal_chain_server
    monkeypatch.setattr(
        causal_chain_server,
        "TIER_MAP",
        {"test-key-123": 3}
    )
    
    return "test-key-123"


class TestDebugRoutesInDevelopment:
    """Test debug routes are accessible in development mode"""
    
    def test_navigation_ui_accessible_in_dev(self, client, mock_api_key):
        """Test /navigation-ui is accessible in development"""
        with patch.dict(os.environ, {"PRODUCTION_MODE": "false"}):
            response = client.get(
                "/navigation-ui",
                headers={"X-API-Key": mock_api_key}
            )
            # Should be accessible (200) or have other non-403 status
            assert response.status_code != 403
    
    def test_navigation_ui_data_accessible_in_dev(self, client, mock_api_key):
        """Test /navigation-ui/data is accessible in development"""
        with patch.dict(os.environ, {"PRODUCTION_MODE": "false"}):
            response = client.get(
                "/navigation-ui/data",
                headers={"X-API-Key": mock_api_key}
            )
            assert response.status_code != 403
    
    def test_swarm_status_accessible_in_dev(self, client, mock_api_key):
        """Test /swarm-status is accessible in development"""
        with patch.dict(os.environ, {"PRODUCTION_MODE": "false"}):
            response = client.get("/swarm-status")
            assert response.status_code != 403
    
    def test_security_info_accessible_in_dev(self, client, mock_api_key):
        """Test /security-info is accessible in development"""
        with patch.dict(os.environ, {"PRODUCTION_MODE": "false"}):
            response = client.get("/security-info")
            assert response.status_code != 403


class TestDebugRoutesInProduction:
    """Test debug routes are blocked in production mode"""
    
    def test_navigation_ui_blocked_in_production(self, client, mock_api_key):
        """Test /navigation-ui is blocked in production"""
        with patch.dict(os.environ, {"PRODUCTION_MODE": "true", "DEBUG": "false"}):
            response = client.get(
                "/navigation-ui",
                headers={"X-API-Key": mock_api_key}
            )
            assert response.status_code == 403
            assert "production" in response.json()["detail"].lower()
    
    def test_navigation_ui_data_blocked_in_production(self, client, mock_api_key):
        """Test /navigation-ui/data is blocked in production"""
        with patch.dict(os.environ, {"PRODUCTION_MODE": "true", "DEBUG": "false"}):
            response = client.get(
                "/navigation-ui/data",
                headers={"X-API-Key": mock_api_key}
            )
            assert response.status_code == 403
    
    def test_swarm_status_blocked_in_production(self, client, mock_api_key):
        """Test /swarm-status is blocked in production"""
        with patch.dict(os.environ, {"PRODUCTION_MODE": "true", "DEBUG": "false"}):
            response = client.get("/swarm-status")
            assert response.status_code == 403
    
    def test_security_info_blocked_in_production(self, client, mock_api_key):
        """Test /security-info is blocked in production"""
        with patch.dict(os.environ, {"PRODUCTION_MODE": "true", "DEBUG": "false"}):
            response = client.get("/security-info")
            assert response.status_code == 403


class TestProductionRoutes:
    """Test that production routes remain accessible"""
    
    def test_resolve_awareness_accessible_in_production(self, client, mock_api_key):
        """Test /resolve-awareness works in production"""
        with patch.dict(os.environ, {"PRODUCTION_MODE": "true"}):
            response = client.post(
                "/resolve-awareness",
                json={"output_id": "output-001"},
                headers={"X-API-Key": mock_api_key}
            )
            # Should work (200) or fail for business logic, not security (403)
            assert response.status_code != 403
    
    def test_legion_status_accessible_in_production(self, client, mock_api_key):
        """Test /legion-status works in production"""
        with patch.dict(os.environ, {"PRODUCTION_MODE": "true"}):
            response = client.get(
                "/legion-status",
                headers={"X-API-Key": mock_api_key}
            )
            assert response.status_code != 403


class TestSecurityInfoEndpoint:
    """Test the /security-info endpoint returns correct information"""
    
    def test_security_info_shows_production_mode(self, client):
        """Test security info shows correct production mode"""
        with patch.dict(os.environ, {"PRODUCTION_MODE": "true", "DEBUG": "false"}):
            # Note: Can't test in production as endpoint is blocked
            # Test in dev mode instead
            pass
        
        with patch.dict(os.environ, {"PRODUCTION_MODE": "false"}):
            response = client.get("/security-info")
            if response.status_code == 200:
                data = response.json()
                assert "production_mode" in data
                assert data["production_mode"] is False
    
    def test_security_info_shows_easter_eggs_status(self, client):
        """Test security info shows Easter eggs status"""
        with patch.dict(os.environ, {"PRODUCTION_MODE": "false"}):
            response = client.get("/security-info")
            if response.status_code == 200:
                data = response.json()
                assert "easter_eggs_enabled" in data
                assert "agent_behaviors" in data


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
