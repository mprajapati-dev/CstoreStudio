from fastapi.testclient import TestClient
from main import app
client = TestClient(app)

def test_create_ticket_without_ai_diagnosis():
    payload = {
        "media_url": "http://localhost:4566/fake.jpg",
        "category": "GAS",
        "manager_note": "No AI diagnosis",
        "store_id": "ST-102",
        "asset_id": "A-002",
        # No ai_diagnosis or ai_estimated_cost
    }
    response = client.post("/tickets", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "ticket_id" in data or "job_id" in data
    assert data["status"] == "OPEN"
    # Should not require ai_diagnosis or ai_estimated_cost
    assert "ai_diagnosis" not in data or data["ai_diagnosis"] in (None, "")

def test_create_ticket_with_ai_diagnosis_informational():
    payload = {
        "media_url": "http://localhost:4566/fake.jpg",
        "category": "GAS",
        "manager_note": "With AI diagnosis informational",
        "store_id": "ST-103",
        "asset_id": "A-003",
        "ai_diagnosis": "Test AI diagnosis informational",
        "ai_estimated_cost": 123.45
    }
    response = client.post("/tickets", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "ticket_id" in data or "job_id" in data
    assert data["status"] == "OPEN"
    # AI diagnosis should be present and informational
    assert data.get("ai_diagnosis", "") == "Test AI diagnosis informational"

def test_create_job():
    payload = {
        "media_url": "http://localhost:4566/fake.jpg",
        "category": "GAS",
        "manager_note": "Test note",
        "store_id": "ST-101",
        "asset_id": "A-001"
    }
    response = client.post("/jobs", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "job_id" in data
    assert data["status"] == "OPEN"

def test_create_ticket():
    payload = {
        "media_url": "http://localhost:4566/fake.jpg",
        "category": "GAS",
        "manager_note": "Test note",
        "store_id": "ST-101",
        "asset_id": "A-001"
    }
    response = client.post("/tickets", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "ticket_id" in data
    assert data["status"] == "OPEN"
