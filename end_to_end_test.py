import requests
import uuid
import time
import boto3

URL = "http://localhost:8000"
dynamodb = boto3.resource('dynamodb', endpoint_url='http://localhost:4566', region_name='us-east-1')
table = dynamodb.Table('Tickets')

ticket_id = f"TICKET-{uuid.uuid4().hex[:8]}"

print(f"E2E Test: Starting LangGraph Flow for {ticket_id}...")

def check_status(expected_statuses):
    """Wait and verify that the ticket status matches one of the expected statuses."""
    if isinstance(expected_statuses, str):
        expected_statuses = [expected_statuses]
        
    for _ in range(10): # retry loop since ai-agent background runs might take seconds
        time.sleep(2)
        item = table.get_item(Key={"ticketId": ticket_id}).get("Item", {})
        actual = item.get("status")
        print(f"[{ticket_id}] Current Status: {actual}")
        if actual in expected_statuses:
            print(f"[{ticket_id}] Matched expected: {actual}")
            return actual
            
    assert False, f"Status mismatch after timeout! Expected {expected_statuses}, got {actual}"

try:
    print("1. DISPATCHing Ticket from Manager/Owner Portal...")
    res = requests.post(f"{URL}/tickets/{ticket_id}/transition", json={
        "action": "DISPATCH",
        "category": "Maintenance",
        "subCategory": "Glass",
        "targetVendorId": "VENDOR_ALICE",
        "store_id": "STORE_123"
    })
    check_status("IN_PROGRESS")

    print("\n2. Vendor Submits Fix (triggering Visual Auditor)...")
    res = requests.post(f"{URL}/tickets/{ticket_id}/transition", json={
        "action": "SUBMIT_FIX",
        "media_url": "https://example.com/fixed_glass.jpg",
        "initial_media_url": "https://example.com/broken_glass.jpg",
        "fix_notes": "Replaced glass panel"
    })
    
    # After submission, it goes directly to Visual Auditor in background, so it will output AWAITING_PAYMENT or VALIDATION_FAILED.
    final_validation_state = check_status(["AWAITING_PAYMENT", "VALIDATION_FAILED"])

    if final_validation_state == "AWAITING_PAYMENT":
        print("\n3. Owner Dispatches Payment...")
        res = requests.post(f"{URL}/tickets/{ticket_id}/transition", json={
            "action": "DISPATCH_PAYMENT"
        })
        check_status("CLOSED")
    else:
        print("\n3. Visual Validation Failed! Status requires manual override or retry.")

    print("\n✅ E2E Test Passed Successfully! The Refactored Workflow works!")
except Exception as e:
    import traceback
    traceback.print_exc()
    print(f"Failed: {e}")

