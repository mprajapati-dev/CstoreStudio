from pydantic import BaseModel
import uuid
import os
import boto3
import json
from decimal import Decimal
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
from prometheus_client import make_asgi_app, Summary, Counter, Gauge

import mcp_server
from agent_graph import app_graph, GraphState

app = FastAPI(title="CstoreStudio AI Agent backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount MCP Server
app.mount("/mcp", mcp_server.create_mcp_app())

# Prometheus metrics setup
app.mount("/metrics", make_asgi_app())

triage_latency = Summary('triage_latency_seconds', 'Time spent in visual triage')
token_usage = Counter('token_usage_total', 'Tokens used by LLMs', ['model'])

# Requested custom metrics
total_tickets_created = Counter('total_tickets_created', 'Total number of tickets created')
repair_delta = Summary('repair_delta', 'Difference between AI Estimate and Final Vendor Price')
agent_actions_total = Counter('agent_actions_total', 'Total agent executions')
agent_success_total = Counter('agent_success_total', 'Total successful agent executions')

AWS_ENDPOINT_URL = os.getenv("AWS_ENDPOINT_URL", "http://localstack:4566")
REGION = os.getenv("AWS_DEFAULT_REGION", "us-east-1")

dynamodb = boto3.resource(
    'dynamodb',
    endpoint_url=AWS_ENDPOINT_URL,
    region_name=REGION,
    aws_access_key_id='test',
    aws_secret_access_key='test'
)

class TransitionRequest(BaseModel):
    action: Optional[str] = None
    media_url: Optional[str] = None
    manager_note: Optional[str] = None
    vendor_bid: Optional[float] = 0.0
    store_id: Optional[str] = None
    category: Optional[str] = None
    sub_category: Optional[str] = None
    target_vendor_id: Optional[str] = None
    ai_diagnosis: Optional[str] = None
    ai_estimated_cost: Optional[float] = None


def process_ticket_background(ticket_id, ticket, req, state, store_id):
    table = dynamodb.Table("Tickets")
    stores_table = dynamodb.Table("Stores")
    try:
        # Run graph
        result = app_graph.invoke(state, {"configurable": {"thread_id": ticket_id}})

        # Log metrics
        agent_actions_total.inc()
        agent_success_total.inc()

        consumed = result.get("credits_consumed", 0)
        from decimal import Decimal
        import uuid
        
        # update vision credit
        if consumed > 0:
            try:
                store_data = stores_table.get_item(Key={"storeId": store_id}).get("Item", {})
                if store_data.get("tier", "STANDARD") == "STANDARD":
                    stores_table.update_item(
                        Key={"storeId": store_id},
                        UpdateExpression="set free_vision_credits = free_vision_credits - :val",
                        ExpressionAttributeValues={":val": consumed}
                    )
            except Exception as e:
                print("Failed to deduct vision credit:", e)

        # If vendor is submitting a bid, append to bids array atomically
        if req.action == "SUBMIT_BID" and req.vendor_bid and req.vendor_bid > 0:
            bid_id = str(uuid.uuid4())
            new_bid = {
                "bidId": bid_id,
                "vendor_id": req.target_vendor_id or ticket.get("targetVendorId", ""),
                "amount": Decimal(str(req.vendor_bid)),
                "eta_days": Decimal(str(result.get("eta_days", 0))),
                "status": "PENDING"
            }
            try:
                table.update_item(
                    Key={"ticketId": ticket_id},
                    UpdateExpression="SET bids = list_append(if_not_exists(bids, :empty_list), :new_bid)",
                    ExpressionAttributeValues={
                        ":empty_list": [],
                        ":new_bid": [new_bid]
                    },
                    ReturnValues="UPDATED_NEW"
                )
            except Exception as e:
                print(f"Failed to append bid: {e}")

        # Merge back to DB (other fields)
        updated_item = {
            "ticketId": ticket_id,
            "status": result.get("status", "OPEN"),
            "mediaUrl": result.get("media_url", ""),
            "managerNote": result.get("manager_note", ""),
            "aiDiagnosis": result.get("ai_diagnosis", ""),
            "aiEstimatedCost": Decimal(str(result.get("ai_estimated_cost", 0.0))),
            "auditFlag": result.get("audit_flag", ""),
            "auditorReasoning": result.get("auditor_reasoning", ""),
            "storeId": store_id,
            "category": req.category or ticket.get("category", ""),
            "subCategory": req.sub_category or ticket.get("subCategory", ""),
            "targetVendorId": req.target_vendor_id or ticket.get("targetVendorId", ""),
            "vendor_id": req.target_vendor_id or ticket.get("targetVendorId", "")
        }

        # If finalizing vendor bid vs AI estimate, log the delta
        if req.action == "APPROVE" and state.get("status") == "PENDING_APPROVAL":
            # Just an approximation
            delta = abs(req.vendor_bid - state.get("ai_estimated_cost", 0.0))
            repair_delta.observe(delta)

        table.put_item(Item=updated_item)
    except Exception as e:
        print(f"Background Graph Execution Error: {str(e)}")

@app.post("/tickets/{ticket_id}/transition")
def transition_ticket(ticket_id: str, req: TransitionRequest, background_tasks: BackgroundTasks):
    table = dynamodb.Table("Tickets")
    # Fetch existing
    from decimal import Decimal
    resp = table.get_item(Key={"ticketId": ticket_id})
    ticket = resp.get("Item")
    
    is_new = False
    if not ticket:
        # Create it if it's the first step (OPEN -> triage)
        ticket = {
            "ticketId": ticket_id,
            "status": "OPEN",
            "aiEstimatedCost": Decimal("0.0"),
            "storeId": req.store_id or "DEFAULT",
            "category": req.category or "",
            "subCategory": req.sub_category or "",
            "targetVendorId": req.target_vendor_id or ""
        }
        is_new = True
        total_tickets_created.inc()
        # Save placeholder immediately so UI can see it
        table.put_item(Item=ticket)

    target_vendor_id = req.target_vendor_id or ticket.get("targetVendorId")
    ticket_category = req.category or ticket.get("category")
    
    if target_vendor_id and ticket_category:
        vendors_table = dynamodb.Table("Vendors")
        vendor = vendors_table.get_item(Key={"vendorId": target_vendor_id}).get("Item")
        if vendor:
            vendor_category = vendor.get("category")
            if vendor_category and vendor_category.upper() != ticket_category.upper():
                raise HTTPException(status_code=400, detail=f"Validation Error: Cannot assign {ticket_category} ticket to {vendor_category} vendor.")
    
    # Fetch Tenant Info for billing stats
    store_id = ticket.get("storeId", "DEFAULT")
    stores_table = dynamodb.Table("Stores")
    store_data = stores_table.get_item(Key={"storeId": store_id}).get("Item", {})
    
    # Reconstruct state for LangGraph
    state_dict = {
        "ticket_id": ticket.get("ticketId"),
        "status": ticket.get("status", "OPEN"),
        "tier": store_data.get("tier", "STANDARD"),
        "free_vision_credits": int(store_data.get("free_vision_credits", 3)),
        "credits_consumed": 0,
        "media_url": req.media_url or ticket.get("mediaUrl", ""),
        "manager_note": req.manager_note or ticket.get("managerNote", ""),
        "ai_diagnosis": req.ai_diagnosis or ticket.get("aiDiagnosis", ""),
        "ai_estimated_cost": float(req.ai_estimated_cost if req.ai_estimated_cost is not None else float(ticket.get("aiEstimatedCost", 0.0))),
        "vendor_bid": req.vendor_bid or 0.0,
        "audit_flag": ticket.get("auditFlag", ""),
        "auditor_reasoning": ticket.get("auditorReasoning", ""),
        "action": req.action
    }
    
    state = GraphState(**state_dict)

    # Queue background task
    background_tasks.add_task(process_ticket_background, ticket_id, ticket, req, state, store_id)

    return {"status": "processing", "message": "Ticket is being processed"}



@app.get("/vendors")
def get_vendors(ids: Optional[str] = None, category: Optional[str] = None):
    try:
        table = dynamodb.Table("Vendors")
        vendors = []
        if ids:
            vendor_ids = ids.split(",")
            for vid in vendor_ids:
                if category:
                    resp = table.get_item(Key={"vendorId": vid, "category": category})
                else:
                    # Fallback scan filter since we need both keys for get_item on composite schemas
                    resp = table.query(
                        KeyConditionExpression=boto3.dynamodb.conditions.Key('vendorId').eq(vid)
                    )
                    items = resp.get("Items", [])
                    if items:
                        resp = {"Item": items[0]}
                    else:
                        resp = {}
                item = resp.get("Item")
                if item:
                    # Convert Decimal to float for JSON serialization
                    if "rating" in item and isinstance(item["rating"], Decimal):
                        item["rating"] = float(item["rating"])
                    if "hourly_rate" in item and isinstance(item["hourly_rate"], Decimal):
                        item["hourly_rate"] = float(item["hourly_rate"])
                    vendors.append(item)
            return vendors
        else:
            response = table.scan()
            vendors = response.get('Items', [])
            # Convert Decimal to float for JSON serialization
            for v in vendors:
                if "rating" in v and isinstance(v["rating"], Decimal):
                    v["rating"] = float(v["rating"])
                if "hourly_rate" in v and isinstance(v["hourly_rate"], Decimal):
                    v["hourly_rate"] = float(v["hourly_rate"])
            if category:
                # Case-insensitive match or exact
                vendors = [v for v in vendors if v.get('category', '').upper() == category.upper()]
            return {"vendors": vendors}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/tickets")
def get_tickets():
    try:
        table = dynamodb.Table("Tickets")
        response = table.scan()
        return {"tickets": response.get('Items', [])}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
def health():
    return {"status": "ok"}

class LoginRequest(BaseModel):
    username: str
    password: str

class CreateUserRequest(BaseModel):
    username: str
    password: str
    role: str
    permissions: List[str] = []
    category: Optional[str] = None
    store_id: Optional[str] = None
    store_ids: Optional[List[str]] = []

@app.post("/users")
def create_user(req: CreateUserRequest):
    try:
        table = dynamodb.Table('Users')
        user_item = {
            "username": req.username,
            "password": req.password,
            "role": req.role,
            "permissions": req.permissions,
            "category": req.category,
            "store_id": req.store_id,
            "store_ids": req.store_ids
        }
        # Filter out None values
        user_item = {k: v for k, v in user_item.items() if v is not None}
        table.put_item(Item=user_item)
        return {"status": "created", "username": req.username}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/login")
def login(req: LoginRequest):
    try:
        table = dynamodb.Table('Users')
        resp = table.get_item(Key={'username': req.username})
        item = resp.get('Item')
        if not item or item.get('password') != req.password:
            raise HTTPException(status_code=401, detail="Invalid username or password")
        
        return {
            "username": item.get('username'),
            "role": item.get('role'),
            "permissions": item.get('permissions', []),
            "category": item.get('category'),
            "store_id": item.get('store_id'),
            "store_name": item.get('store_name'),
            "store_ids": item.get('store_ids', [])
        }
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"ERROR: {str(e)}")



# --- Categories Endpoint ---
@app.get("/categories")
def get_categories():
    table = dynamodb.Table("Categories")
    response = table.scan()
    categories = response.get("Items", [])
    # Return full category info including preferred_vendor_ids
    return {
        cat["category"]: {
            "sub_categories": cat.get("sub_categories", []),
            "preferred_vendor_ids": cat.get("preferred_vendor_ids", [])
        }
        for cat in categories
    }
