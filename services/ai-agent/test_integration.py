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
