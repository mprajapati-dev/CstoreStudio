from fastapi.testclient import TestClient
from unittest.mock import patch
import sys
import os

# Add parent directory to path so we can import main
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app

client = TestClient(app)

def test_health_check():
    """Test the /health endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

@patch("main.litellm.completion")
@patch("main.dynamodb.put_item")
def test_triage_endpoint_success(mock_put_item, mock_completion):
    """Test the /triage endpoint and LangGraph workflow with mocked LLM and DB"""
    # 1. Setup mock LLM response
    class MockMessage:
        content = "The media shows a broken pump. Needs expensive repairs."
    class MockChoice:
        message = MockMessage()
    class MockUsage:
        total_tokens = 50
    class MockResponse:
        choices = [MockChoice()]
        usage = MockUsage()
        
    mock_completion.return_value = MockResponse()
    mock_put_item.return_value = {}

    # 2. Test the API call
    payload = {"media_url": "http://localhost:4566/cstore-media/test-img.png"}
    response = client.post("/triage", json=payload)
    
    # 3. Assertions
    assert response.status_code == 200
    data = response.json()
    assert "job_id" in data
    
    # Because our mock response included the word "expensive", our business_logic 
    # should flag it as "Needs Owner"
    assert data["status"] == "Needs Owner"
    assert data["details"] == "The media shows a broken pump. Needs expensive repairs."
    
    # Verify the mock DB was called
    mock_put_item.assert_called_once()
