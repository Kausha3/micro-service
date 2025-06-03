import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_root_endpoint():
    """Test the root health check endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "message" in data
    assert "version" in data


def test_chat_endpoint_basic():
    """Test basic chat functionality."""
    response = client.post("/chat", json={
        "message": "Hello"
    })
    assert response.status_code == 200
    data = response.json()
    assert "reply" in data
    assert "session_id" in data
    assert isinstance(data["reply"], str)
    assert len(data["reply"]) > 0


def test_chat_endpoint_with_session():
    """Test chat with existing session ID."""
    # First message to get session ID
    response1 = client.post("/chat", json={
        "message": "Hello"
    })
    assert response1.status_code == 200
    session_id = response1.json()["session_id"]

    # Second message with session ID
    response2 = client.post("/chat", json={
        "message": "My name is John",
        "session_id": session_id
    })
    assert response2.status_code == 200
    data = response2.json()
    assert data["session_id"] == session_id


def test_inventory_endpoint():
    """Test inventory endpoint."""
    response = client.get("/inventory")
    assert response.status_code == 200
    data = response.json()
    assert "available_units" in data
    assert isinstance(data["available_units"], list)


def test_chat_endpoint_invalid_json():
    """Test chat endpoint with invalid JSON."""
    response = client.post("/chat", json={})
    assert response.status_code == 422  # Validation error


def test_session_endpoint_not_found():
    """Test session endpoint with non-existent session."""
    response = client.get("/sessions/non-existent-session")
    assert response.status_code == 404


def test_chat_flow_name_collection():
    """Test the chat flow for name collection."""
    # Start conversation
    response1 = client.post("/chat", json={"message": "Hello"})
    session_id = response1.json()["session_id"]

    # Provide name
    response2 = client.post("/chat", json={
        "message": "John Doe",
        "session_id": session_id
    })
    assert response2.status_code == 200
    reply = response2.json()["reply"].lower()
    assert "email" in reply


def test_chat_flow_email_validation():
    """Test email validation in chat flow."""
    # Start conversation and provide name
    response1 = client.post("/chat", json={"message": "Hello"})
    session_id = response1.json()["session_id"]

    client.post("/chat", json={
        "message": "John Doe",
        "session_id": session_id
    })

    # Provide invalid email
    response3 = client.post("/chat", json={
        "message": "invalid-email",
        "session_id": session_id
    })
    assert response3.status_code == 200
    reply = response3.json()["reply"].lower()
    assert "valid email" in reply


if __name__ == "__main__":
    pytest.main([__file__])
