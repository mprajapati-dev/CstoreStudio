import pytest
from unittest.mock import patch, MagicMock
from agent_graph import app_graph, GraphState

@pytest.fixture
def mock_litellm():
    with patch("agent_graph.litellm.completion") as mock_completion:
        yield mock_completion

def test_supervisor_routes_to_triage(mock_litellm):
    """
    Test the Supervisor Node: Verify that a ticket with status 'OPEN' 
    and a media_url correctly routes to the 'TriageNode' (triage_agent).
    """
    # Mock the LLM JSON response for the Vision Triage
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = '```json\n{"diagnosis": "Broken POS screen", "estimated_cost": 250.0}\n```'
    mock_litellm.return_value = mock_response

    initial_state = {
        "ticket_id": "test-triage-001",
        "status": "OPEN",
        "media_url": "https://s3.amazonaws.com/cstore-media/broken.jpg",
        "manager_note": "System won't turn on",
        "ai_diagnosis": None,
        "ai_estimated_cost": 0.0,
        "vendor_bid": 0.0,
        "audit_flag": None,
        "action": None
    }
    
    config = {"configurable": {"thread_id": "thread-test-triage-001"}}
    final_state = app_graph.invoke(initial_state, config=config)

    # After triage, status becomes AWAITING_BIDS and graph stops because no vendor bid is present
    assert final_state["status"] == "AWAITING_BIDS"
    assert final_state["ai_estimated_cost"] == 250.0
    assert final_state["ai_diagnosis"] == "Broken POS screen"
    mock_litellm.assert_called_once()

def test_auditor_node(mock_litellm):
    """
    Test the Auditor Node: ai_estimated_cost is $100 and vendor_bid is $500. 
    Assert that the ticket state changes to HIGH_RISK_REASONING_REQUIRED (Flagged for Review).
    """
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = "Internal Monologue: Bid is way too high."
    mock_litellm.return_value = mock_response

    initial_state = {
        "ticket_id": "test-audit-002",
        "status": "AWAITING_BIDS",
        "media_url": None,
        "manager_note": None,
        "ai_diagnosis": "Fix A/C leak",
        "ai_estimated_cost": 100.0,
        "vendor_bid": 500.0,
        "audit_flag": None,
        "action": None
    }
    
    config = {"configurable": {"thread_id": "thread-test-audit-002"}}
    
    final_state = app_graph.invoke(initial_state, config=config)
    
    # Delta is (500-100)/100 = 4.0 > 0.25, so audit_flag should be HIGH_RISK_REASONING_REQUIRED
    # And status transitions to PENDING_APPROVAL
    assert final_state["status"] == "PENDING_APPROVAL"
    assert final_state["audit_flag"] == "HIGH_RISK_REASONING_REQUIRED"

def test_graph_interrupt(mock_litellm):
    """
    Test the Interrupt: Verify that the graph pauses and waits for 'Owner Approval' 
    before moving to 'IN_PROGRESS'.
    """
    initial_state = {
        "ticket_id": "test-interrupt-003",
        "status": "PENDING_APPROVAL",
        "media_url": None,
        "manager_note": None,
        "ai_diagnosis": "Plumbing",
        "ai_estimated_cost": 200.0,
        "vendor_bid": 210.0,
        "audit_flag": "OK",
        "action": None
    }
    
    config = {"configurable": {"thread_id": "thread-test-interrupt-003"}}
    
    # Step 1: Submit state. Submitting PENDING_APPROVAL causes supervisor to route to owner_approval.
    # owner_approval is in interrupt_before.
    final_state = app_graph.invoke(initial_state, config=config)
    
    # Verify graph interrupted at owner_approval
    app_state = app_graph.get_state(config)
    assert app_state.next == ("owner_approval",), "Graph should pause before owner_approval node"
    
    # Original state values should remain untouched while paused
    assert final_state["status"] == "PENDING_APPROVAL"

    # Step 2: Resume with the Manager/Owner action
    resume_state = {"action": "APPROVE"}
    
    final_state_after_resume = app_graph.invoke(resume_state, config=config)
    
    # owner_approval step sets status to IN_PROGRESS upon action=APPROVE
    assert final_state_after_resume["status"] == "IN_PROGRESS"
