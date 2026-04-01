import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from main import app, transition_ticket, TransitionRequest

client = TestClient(app)

@patch('main.dynamodb')
@patch('main.app_graph')
def test_manager_assigns_hvac_to_gas_vendor_throws_validation_error(mock_app_graph, mock_dynamodb):
    # Mock DynamoDB Tables
    mock_tickets_table = MagicMock()
    mock_vendors_table = MagicMock()
    mock_stores_table = MagicMock()
    
    def mock_table(table_name):
        if table_name == "Tickets":
            return mock_tickets_table
        elif table_name == "Vendors":
            return mock_vendors_table
        elif table_name == "Stores":
            return mock_stores_table
        return MagicMock()
        
    mock_dynamodb.Table.side_effect = mock_table

    # Existing ticket is HVAC
    mock_tickets_table.get_item.return_value = {
        "Item": {
            "ticketId": "ticket-123",
            "category": "HVAC",
            "targetVendorId": "vendor-999"
        }
    }
    
    # Target vendor is GAS
    mock_vendors_table.get_item.return_value = {
        "Item": {
            "vendorId": "vendor-999",
            "category": "GAS"
        }
    }
    
    response = client.post("/tickets/ticket-123/transition", json={
        "action": "ASSIGN",
        "category": "HVAC",
        "target_vendor_id": "vendor-999"
    })
    
    assert response.status_code == 400
    assert "Cannot assign HVAC ticket to GAS vendor" in response.json()["detail"]

