import pytest
import json
from unittest.mock import patch, MagicMock
from agent_graph import app_graph, GraphState

# Small 1x1 valid base64 transparent PNG
SAMPLE_B64_IMAGE = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII="

@pytest.fixture
def mock_litellm():
    with patch("agent_graph.litellm.completion") as mock_completion:
        yield mock_completion

def test_visual_verification_success(mock_litellm):
    """
    Test Case: AI verifies the image successfully (confidence >= 0.5).
    Asserts the ticket progresses to 'AWAITING_PAYMENT'.
    """
    # Mock Litellm responding positively
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = '```json\n{"verified": true, "confidence": 0.95}\n```'
    mock_litellm.return_value = mock_response

    initial_state = {
        "ticket_id": "test-visual-001",
        "status": "PENDING_VALIDATION",
        "media_url": SAMPLE_B64_IMAGE,
        "manager_note": "Vendor submitted fix",
        "ai_diagnosis": "Broken Register",
        "ai_estimated_cost": 500.0,
        "vendor_bid": 500.0,
        "audit_flag": "OK",
        "action": "SUBMIT_FIX"
    }
    
    config = {"configurable": {"thread_id": "thread-test-visual-001"}}
    
    # Run graph - routing will take it from supervisor -> manager_validation
    final_state = app_graph.invoke(initial_state, config=config)
    
    # Should move to AWAITING_PAYMENT due to confidence 0.95
    assert final_state["status"] == "AWAITING_PAYMENT"
    mock_litellm.assert_called_once()

def test_visual_verification_failure(mock_litellm):
    """
    Test Case: AI fails the verification (confidence < 0.5 or verified: false).
    Asserts the system triggers a notification to Manager instead of moving to AWAITING_PAYMENT.
    """
    # Mock Litellm responding negatively
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = '```json\n{"verified": false, "confidence": 0.35}\n```'
    mock_litellm.return_value = mock_response

    initial_state = {
        "ticket_id": "test-visual-fail-002",
        "status": "PENDING_VALIDATION",
        "media_url": SAMPLE_B64_IMAGE,
        "manager_note": "Vendor says fixed, looks messy",
        "ai_diagnosis": "Plumbing Leak",
        "ai_estimated_cost": 250.0,
        "vendor_bid": 250.0,
        "audit_flag": "OK",
        "action": "SUBMIT_FIX"
    }
    
    config = {"configurable": {"thread_id": "thread-test-visual-fail-002"}}
    
    # Run graph
    final_state = app_graph.invoke(initial_state, config=config)
    
    # Verification failed: state changes to VALIDATION_FAILED, and audit flag raises
    assert final_state["status"] == "VALIDATION_FAILED"
    assert final_state["audit_flag"] == "MANAGER_NOTIFICATION_TRIGGERED"
    mock_litellm.assert_called_once()
