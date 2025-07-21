import pytest
from fastapi.testclient import TestClient
from app import app

client = TestClient(app)

def test_health_check():
    """Test the health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy", "service": "subtraction-service"}

def test_subtraction_success():
    """Test successful subtraction operation."""
    response = client.get("/?first_number=10&second_number=3")
    assert response.status_code == 200
    data = response.json()
    assert data["result"] == 7.0
    assert data["operation"] == "subtraction"
    assert data["first_number"] == 10.0
    assert data["second_number"] == 3.0

def test_subtraction_with_decimals():
    """Test subtraction with decimal numbers."""
    response = client.get("/?first_number=7.5&second_number=2.5")
    assert response.status_code == 200
    data = response.json()
    assert data["result"] == 5.0

def test_subtraction_negative_result():
    """Test subtraction resulting in negative number."""
    response = client.get("/?first_number=5&second_number=10")
    assert response.status_code == 200
    assert response.json()["result"] == -5.0

def test_subtraction_negative_numbers():
    """Test subtraction with negative numbers."""
    response = client.get("/?first_number=-10&second_number=-5")
    assert response.status_code == 200
    assert response.json()["result"] == -5.0

def test_subtraction_default_values():
    """Test subtraction with default values (0-0)."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["result"] == 0.0