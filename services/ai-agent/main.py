import os
import uuid
import boto3
import json
from decimal import Decimal
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
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

AWS_ENDPOINT_URL = os.getenv("AWS_ENDPOINT_URL", "http://localhost:4566")
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

@app.post("/tickets/{ticket_id}/transition")
def transition_ticket(ticket_id: str, req: TransitionRequest):
    table = dynamodb.Table("Tickets")
    # Fetch existing
    resp = table.get_item(Key={"ticketId": ticket_id})
    ticket = resp.get("Item")
    
    is_new = False
    if not ticket:
        # Create it if it's the first step (OPEN -> triage)
        ticket = {
            "ticketId": ticket_id,
            "status": "OPEN",
            "aiEstimatedCost": Decimal("0.0"),
        }
        is_new = True
        total_tickets_created.inc()
    
    # Reconstruct state for LangGraph
    state = GraphState(
        ticket_id=ticket.get("ticketId"),
        status=ticket.get("status", "OPEN"),
        media_url=req.media_url or ticket.get("mediaUrl"),
        manager_note=req.manager_note or ticket.get("managerNote"),
        ai_diagnosis=ticket.get("aiDiagnosis"),
        ai_estimated_cost=float(ticket.get("aiEstimatedCost", 0.0)),
        vendor_bid=req.vendor_bid or 0.0,
        audit_flag=ticket.get("auditFlag"),
        action=req.action
    )
    
    config = {"configurable": {"thread_id": ticket_id}}
    
    try:
        agent_actions_total.inc()
        # Run graph
        result = app_graph.invoke(state, config=config)
        agent_success_total.inc()
        
        # Merge back to DB
        updated_item = {
            "ticketId": ticket_id,
            "status": result.get("status"),
            "mediaUrl": result.get("media_url", ""),
            "managerNote": result.get("manager_note", ""),
            "aiDiagnosis": result.get("ai_diagnosis", ""),
            "aiEstimatedCost": Decimal(str(result.get("ai_estimated_cost", 0.0))),
            "auditFlag": result.get("audit_flag", "")
        }
        
        # If finalizing vendor bid vs AI estimate, log the delta
        if req.action == "APPROVE" and state["status"] == "PENDING_APPROVAL":
            delta = abs(req.vendor_bid - state["ai_estimated_cost"])
            repair_delta.observe(delta)

        table.put_item(Item=updated_item)
        return {"status": "ok", "state": result}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Graph Execution Error: {str(e)}")

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
            "permissions": item.get('permissions', [])
        }
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"ERROR: {str(e)}")
