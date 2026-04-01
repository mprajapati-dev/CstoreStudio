import pytest
from unittest.mock import patch, MagicMock

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from agent_graph import visual_auditor_agent, GraphState

@patch('agent_graph.litellm.completion')
def test_auditor_agent_visual_verification_fails(mock_completion):
    mock_response = MagicMock()
    mock_choice = MagicMock()
    mock_choice.message.content = '{"verified": false, "confidence": 0.99, "reasoning": "Photos are identical. No work was performed."}'
    mock_response.choices = [mock_choice]
    mock_completion.return_value = mock_response

    state = GraphState(
        ticket_id="ticket-123",
        status="PENDING_VALIDATION",
        initial_media_url="http://example.com/broken.jpg",
        media_url="http://example.com/broken.jpg", 
        action="SUBMIT_FIX",
        credits_consumed=0
    )

    new_state = visual_auditor_agent(state)

    assert new_state.get("status") != "AWAITING_PAYMENT", "Ticket should NOT proceed to AWAITING_PAYMENT"
    assert new_state.get("status") == "VALIDATION_FAILED"
    assert new_state.get("audit_flag") == "MANAGER_NOTIFICATION_TRIGGERED"

