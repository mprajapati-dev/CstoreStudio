import pytest
import os
import boto3
import json
import uuid
from decimal import Decimal
from fastapi.testclient import TestClient

# Ensure tests point to localstack
os.environ["AWS_ENDPOINT_URL"] = "http://localhost:4566"
os.environ["AWS_REGION"] = "us-east-1"

from main import app
from mcp_server import handle_call_tool
from unittest.mock import patch, MagicMock

client = TestClient(app)

# Helper function to get DynamoDB resource
def get_dynamo():
    return boto3.resource(
        "dynamodb",
        endpoint_url="http://localhost:4566",
        region_name="us-east-1",
        aws_access_key_id="test",
        aws_secret_access_key="test"
    )

@pytest.fixture(autouse=True)
def setup_tables():
    """Ensure tables exist before tests run."""
    dynamodb = get_dynamo()
    
    tables_to_create = [
        ('Vendors', 'vendorId'),
        ('Tickets', 'ticketId'),
        ('Bids', 'bidId')
    ]
    
    for table_name, hash_key in tables_to_create:
        try:
            dynamodb.create_table(
                TableName=table_name,
                KeySchema=[{'AttributeName': hash_key, 'KeyType': 'HASH'}],
                AttributeDefinitions=[{'AttributeName': hash_key, 'AttributeType': 'S'}],
                BillingMode='PAY_PER_REQUEST'
            )
        except dynamodb.meta.client.exceptions.ResourceInUseException:
            pass
        
    yield
    
    # Cleanup data after test
    for table_name, hash_key in tables_to_create:
        table = dynamodb.Table(table_name)
        scan = table.scan()
        with table.batch_writer() as batch:
            for each in scan.get('Items', []):
                batch.delete_item(Key={hash_key: each[hash_key]})


@pytest.mark.asyncio
async def test_mcp_fetch_vendors_by_category():
    """
    Test Case: Create a dummy vendor in the Vendors table, 
    then call the MCP tool fetch_vendors (category). 
    Assert the returned list contains the dummy vendor.
    """
    dynamodb = get_dynamo()
    vendor_table = dynamodb.Table('Vendors')
    
    dummy_id = str(uuid.uuid4())
    vendor_table.put_item(Item={
        "vendorId": dummy_id,
        "name": "Integration Test Plumbers",
        "category": "Plumbing",
        "rating": Decimal("5.0")
    })
    
    result = await handle_call_tool("fetch_vendors", {"category": "Plumbing"})
    
    assert len(result) == 1
    content_str = result[0].text
    vendors_returned = json.loads(content_str)
    
    found = any(v["vendorId"] == dummy_id for v in vendors_returned)
    assert found is True
    assert vendors_returned[0]["category"] == "Plumbing"

@patch("main.app_graph.invoke") 
def test_create_ticket_via_fastapi(mock_invoke):
    """
    Test Case: Simulate a Manager creating a ticket and verify 
    the record exists in the Tickets table with the correct UUID.
    """
    mock_invoke.return_value = {
        "status": "OPEN", 
        "media_url": "s3://mockUrl", 
        "manager_note": "A mock note",
        "ai_diagnosis": "",
        "ai_estimated_cost": 0.0,
        "audit_flag": ""
    }

    ticket_id = f"test-ticket-{uuid.uuid4()}"
    payload = {
        "action": "START",
        "media_url": "s3://mockUrl",
        "manager_note": "A mock note"
    }
    
    response = client.post(f"/tickets/{ticket_id}/transition", json=payload)
    assert response.status_code == 200
    
    dynamodb = get_dynamo()
    ticket_table = dynamodb.Table('Tickets')
    db_response = ticket_table.get_item(Key={"ticketId": ticket_id})
    
    assert "Item" in db_response
    item = db_response["Item"]
    assert item["ticketId"] == ticket_id
    assert item["status"] == "OPEN"
    assert item["mediaUrl"] == "s3://mockUrl"

@pytest.mark.asyncio
async def test_mcp_post_bid():
    """
    Test Case: Tests post_bid MCP server tool properly writes the bid logic to DynamoDB.
    """
    ticket_id = f"ticket-{uuid.uuid4()}"
    vendor_id = f"vendor-{uuid.uuid4()}"
    
    # Call MCP tool directly
    result = await handle_call_tool("post_bid", {
        "ticket_id": ticket_id,
        "vendor_id": vendor_id,
        "amount": 450.00
    })
    
    assert len(result) == 1
    response_json = json.loads(result[0].text)
    assert response_json.get("success") is True
    
    bid_id = response_json.get("bid_id")
    assert bid_id is not None
    
    # Verify the bid was properly inserted into the DynamoDB `Bids` table
    dynamodb = get_dynamo()
    bids_table = dynamodb.Table('Bids')
    db_response = bids_table.get_item(Key={"bidId": bid_id})
    
    assert "Item" in db_response
    item = db_response["Item"]
    assert item["ticketId"] == ticket_id
    assert item["vendorId"] == vendor_id
    assert float(item["amount"]) == 450.00
    assert item["status"] == "PENDING"

@pytest.mark.asyncio
async def test_mcp_multitenant_isolation():
    """
    Test Case: Ensure that a Manager from 'Store A' cannot see or modify 
    a Ticket belonging to 'Store B' via the MCP tools.
    """
    dynamodb = get_dynamo()
    ticket_table = dynamodb.Table('Tickets')
    
    # Store B's private ticket
    ticket_id_store_b = f"ticket-b-{uuid.uuid4()}"
    ticket_table.put_item(Item={
        "ticketId": ticket_id_store_b,
        "storeId": "Store-B",
        "status": "OPEN",
        "managerNote": "Leaky roof"
    })
    
    # 1. Store A tries to GET Store B's ticket context using MCP
    get_res = await handle_call_tool("get_ticket_context", {
        "ticket_id": ticket_id_store_b,
        "caller_store_id": "Store-A"
    })
    
    get_data = json.loads(get_res[0].text)
    assert "error" in get_data
    assert "Unauthorized" in get_data["error"]
    
    # 2. Store A tries to UPDATE Store B's ticket state using MCP
    update_res = await handle_call_tool("update_status", {
        "ticket_id": ticket_id_store_b,
        "new_status": "CLOSED",
        "caller_store_id": "Store-A"
    })
    
    update_data = json.loads(update_res[0].text)
    assert "error" in update_data
    assert "Unauthorized" in update_data["error"]
    
    # Verify the item in DynamoDB remained untouched natively
    verify_resp = ticket_table.get_item(Key={"ticketId": ticket_id_store_b})
    assert verify_resp["Item"]["status"] == "OPEN"

@pytest.mark.asyncio
async def test_vendor_bidding_workflow_concurrency():
    """
    Test Case: Simulate 3 vendors submitting bids simultaneously.
    Ensure atomic updates in DynamoDB and correct sorting by Best Value.
    """
    import asyncio
    dynamodb = get_dynamo()
    ticket_table = dynamodb.Table('Tickets')
    
    # Create an initial ticket
    ticket_id = f"ticket-bidding-{uuid.uuid4()}"
    store_id = "Store-BidTest"
    ticket_table.put_item(Item={
        "ticketId": ticket_id,
        "storeId": store_id,
        "status": "OPEN",
        "managerNote": "Fix AC",
        "bids": []
    })
    
    # Simulate concurrent bid requests
    async def make_bid(vendor_id, amount, eta_days):
        return await handle_call_tool("submit_bid", {
            "ticket_id": ticket_id,
            "vendor_id": vendor_id,
            "bid_amount": amount,
            "eta_days": eta_days
        })

    # vendor1: amount=500, eta=2
    # vendor2: amount=300, eta=5
    # vendor3: amount=450, eta=1
    
    res1, res2, res3 = await asyncio.gather(
        make_bid("vendor1", 500, 2),
        make_bid("vendor2", 300, 5),
        make_bid("vendor3", 450, 1)
    )
    
    # 1. Assert: Ensure the Tickets table appended all three bids without overwriting
    verify_resp = ticket_table.get_item(Key={"ticketId": ticket_id})
    bids = verify_resp.get("Item", {}).get("bids", [])
    
    assert len(bids) == 3, f"Expected 3 bids, but found {len(bids)}. Concurrency overwritten data!"
    
    vendor_ids = [b["vendor_id"] for b in bids]
    assert "vendor1" in vendor_ids
    assert "vendor2" in vendor_ids
    assert "vendor3" in vendor_ids

    # 2. Assert: Verify the Owner portal sorting algorithm (Best Value = lowest amount + penalty per day)
    # Assuming the algorithm returns them sorted or we verify the get_ticket_context returns sorted
    context_res = await handle_call_tool("get_ticket_context", {
        "ticket_id": ticket_id,
        "caller_store_id": store_id
    })
    
    ticket_data = json.loads(context_res[0].text)
    returned_bids = ticket_data.get("bids", [])
    
    assert len(returned_bids) == 3
    
    # Expected values calculation: formula = amount + (eta_days * 50)
    # vendor1 => 500 + (2*50) = 600
    # vendor2 => 300 + (5*50) = 550
    # vendor3 => 450 + (1*50) = 500
    # Sorted order (lowest value first): vendor3, vendor2, vendor1
    
    returned_vendor_ids = [b["vendor_id"] for b in returned_bids]
    assert returned_vendor_ids == ["vendor3", "vendor2", "vendor1"], f"Sort failed. Expected ['vendor3', 'vendor2', 'vendor1'], got {returned_vendor_ids}"

    
