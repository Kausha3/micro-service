"""
Test for the health endpoint functionality.

This test verifies that the /health endpoint works correctly for wake-up pings
and health monitoring.
"""

import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_health_endpoint():
    """Test that the health endpoint returns the correct response."""
    response = client.get("/health")
    
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_health_endpoint_headers():
    """Test that the health endpoint has correct headers for CORS."""
    # Test with Origin header to trigger CORS
    response = client.get("/health", headers={"Origin": "http://localhost:3000"})

    assert response.status_code == 200
    # The response should include CORS headers due to our middleware
    assert "access-control-allow-origin" in response.headers


def test_root_endpoint_still_works():
    """Test that the original root endpoint still works."""
    response = client.get("/")
    
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "status" in data
    assert data["status"] == "healthy"


def test_health_vs_root_response_difference():
    """Test that health and root endpoints return different responses."""
    health_response = client.get("/health")
    root_response = client.get("/")
    
    assert health_response.status_code == 200
    assert root_response.status_code == 200
    
    # Health endpoint should be simpler
    health_data = health_response.json()
    root_data = root_response.json()
    
    assert health_data == {"status": "ok"}
    assert len(root_data) > len(health_data)  # Root has more information


if __name__ == "__main__":
    pytest.main([__file__])
