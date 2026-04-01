import pytest
import os
import sys
import boto3
import json
import uuid

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fastapi.testclient import TestClient
from main import app
from mcp_server import handle_call_tool

client = TestClient(app)

AWS_ENDPOINT_URL = "http://localhost:4566"
REGION = "us-east-1"

@pytest.fixture(scope="module")
def dynamodb():
    return boto3.resource(
        'dynamodb',
        endpoint_url=AWS_ENDPOINT_URL,
        region_name=REGION,
        aws_access_key_id='test',
        aws_secret_access_key='test'
    )

@pytest.mark.asyncio
async def test_mcp_fetch_vendors(dynamodb):
    vendors_table = dynamodb.Table("Vendors")
    dummy_vendor_id = f"vendor-test-{uuid.uuid4()}"
    vendors_table.put_item(Item={
        "vendorId": dummy_vendor_id,
        "name": "Test Vendor",
        "category": "TEST_CATEGORY"
    })
    
    # Call MCP directly to avoid spinning up SSE streams in simple tests
    result = await handle_call_tool("fetch_vendors", {"category": "TEST_CATEGORY"})
    
    assert len(result) == 1
    assert result[0].type == "text"
    
    parsed_vendors = json.loads(result[0].text)
    assert any(v["vendorId"] == dummy_vendor_id for v in parsed_vendors)
    
    # Cleanup
    vendors_table.delete_item(Key={"vendorId": dummy_vendor_id})

def test_manager_creates_ticket_and_persists_in_db(dynamodb):
    ticket_id = f"ticket-test-{uuid.uuid4()}"
    
    response = client.post(f"/tickets/{ticket_id}/transition", json={
        "action": "CREATE",
        "store_id": "STORE_001",
        "category": "PLUMBING",
        "manager_note": "Leaky pipe test"
    })
    assert response.status_code == 200
    
    tickets_table = dynamodb.Table("Tickets")
    db_response = tickets_table.get_item(Key={"ticketId": ticket_id})
    assert "Item" in db_response
    assert db_response["Item"]["ticketId"] == ticket_id
    assert db_response["Item"]["storeId"] == "STORE_001"
    assert db_response["Item"]["category"] == "PLUMBING"
    
    # Cleanup
    tickets_table.delete_item(Key={"ticketId": ticket_id})
