import re

with open('services/ai-agent/main.py', 'r') as f:
    code = f.read()

# 1. Add payment_processing node before persistence
patch_nodes = """
def payment_processing(state: JobState):
    print("STARTING payment_processing")
    # Mocking a payment
    # This state node represents calling Stripe or an external AP AP system
    state["approval_status"] = "Payment Complete"
    return state

def persistence(state: JobState):
"""

code = code.replace("def persistence(state: JobState):", patch_nodes)

# 2. Add an endpoint
patch_endpoint = """
@app.post("/jobs/{job_id}/pay")
def pay_vendor(job_id: str):
    try:
        # Mock payment by manually updating status directly (or invoking the node)
        dynamodb.update_item(
            TableName='Jobs',
            Key={'jobId': {'S': job_id}},
            UpdateExpression='SET approvalStatus = :status',
            ExpressionAttributeValues={
                ':status': {'S': 'Payment Complete'}
            }
        )
        return {"status": "ok", "message": "Payment Complete"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"ERROR: {str(e)}")

@app.post("/jobs/{job_id}/ai-diagnose")
"""

code = code.replace('@app.post("/jobs/{job_id}/ai-diagnose")', patch_endpoint)

with open('services/ai-agent/main.py', 'w') as f:
    f.write(code)

