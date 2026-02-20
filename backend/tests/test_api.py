"""Tests for API endpoints."""
from datetime import date

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_endpoint():
    """Test health check returns healthy."""
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_tickers_endpoint():
    """Test tickers list returns popular stocks."""
    response = client.get("/api/tickers")
    assert response.status_code == 200
    data = response.json()
    assert "popular" in data
    assert len(data["popular"]) > 0
    assert data["popular"][0]["symbol"] == "AAPL"


def test_backtest_validation():
    """Test backtest validates request."""
    response = client.post("/api/backtest", json={})
    assert response.status_code == 422  # Validation error
