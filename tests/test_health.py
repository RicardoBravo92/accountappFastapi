"""Tests for health check and root endpoints - mirrors akaunting test_health.php patterns."""
from fastapi.testclient import TestClient

from app.main import app


def test_health_check():
    """Test that health endpoint returns 200 with status ok."""
    with TestClient(app) as client:
        response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "version" in data
    assert "environment" in data


def test_root_endpoint():
    """Test that root endpoint returns API information."""
    with TestClient(app) as client:
        response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "version" in data
    assert "docs_url" in data


def test_api_v1_routes_exist():
    """Test that all API v1 routes are registered."""
    with TestClient(app) as client:
        # Auth routes
        resp = client.post("/api/v1/auth/login", data={
            "username": "test@example.com",
            "password": "wrong"
        })
        assert resp.status_code == 401

        # Company routes (should require auth)
        resp = client.get("/api/v1/companies")
        assert resp.status_code == 401

        # Contact routes
        resp = client.get("/api/v1/contacts?company_id=1")
        assert resp.status_code == 401

        # Account routes
        resp = client.get("/api/v1/accounts?company_id=1")
        assert resp.status_code == 401
