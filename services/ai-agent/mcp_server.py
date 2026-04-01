import os
import boto3
from boto3.dynamodb.conditions import Attr
from typing import Optional, List, Dict, Any
from mcp.server import Server
import mcp.types as types
from decimal import Decimal
import json

# Setup boto3 resource
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
AWS_ENDPOINT_URL = os.getenv("AWS_ENDPOINT_URL", "http://localhost:4566")

dynamodb = boto3.resource(
    "dynamodb",
    region_name=AWS_REGION,
    endpoint_url=AWS_ENDPOINT_URL,
    aws_access_key_id="test",
    aws_secret_access_key="test"
)

# Initialize MCP server
mcp = Server("cstore-mcp-server")

class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super(DecimalEncoder, self).default(obj)

@mcp.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="fetch_vendors",
            description="Returns a list of vendors filtered by category from DynamoDB.",
            inputSchema={
                "type": "object",
                "properties": {
                    "category": {"type": "string", "description": "The trade category (e.g. 'Plumbing', 'HVAC', etc.)"}
                },
                "required": ["category"]
            }
        ),
        types.Tool(
            name="post_bid",
            description="Saves a vendor bid.",
            inputSchema={
                "type": "object",
                "properties": {
                    "ticket_id": {"type": "string"},
                    "vendor_id": {"type": "string"},
                    "amount": {"type": "number"},
                    "eta_days": {"type": "number"}
                },
                "required": ["ticket_id", "vendor_id", "amount", "eta_days"]
            }
        ),
        types.Tool(
            name="get_ticket_context",
            description="Pulls the ticket description, AI estimates, and previous maintenance history for that specific store.",
            inputSchema={
                "type": "object",
                "properties": {
                    "ticket_id": {"type": "string"},
                    "caller_store_id": {"type": "string"}
                },
                "required": ["ticket_id"]
            }
        ),
        types.Tool(
            name="update_status",
            description="Moves the ticket through the state machine.",
            inputSchema={
                "type": "object",
                "properties": {
                    "ticket_id": {"type": "string"},
                    "new_status": {"type": "string", "description": "The new status (e.g., AWAITING_BIDS, IN_PROGRESS, CLOSED)"},
                    "caller_store_id": {"type": "string"}
                },
                "required": ["ticket_id", "new_status"]
            }
        )
    ]

@mcp.call_tool()
async def handle_call_tool(
    name: str, arguments: dict | None
) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    if not arguments:
        raise ValueError("Missing arguments")

    if name == "fetch_vendors":
        category = arguments.get("category")
        table = dynamodb.Table("Vendors")
        
        # Scans or queries the table to filter by category
        # seed_db.py sets "category" string field
        response = table.scan(
            FilterExpression=boto3.dynamodb.conditions.Attr("category").eq(category)
        )
        vendors = response.get("Items", [])
        return [types.TextContent(type="text", text=json.dumps(vendors, cls=DecimalEncoder))]

    elif name == "post_bid":
        ticket_id = arguments.get("ticket_id")
        vendor_id = arguments.get("vendor_id")
        amount = arguments.get("amount")
        eta_days = arguments.get("eta_days")
        
        import uuid
        bid_id = str(uuid.uuid4())
        
        ticket_table = dynamodb.Table("Tickets")
        new_bid = {
            "bidId": bid_id,
            "vendor_id": vendor_id,
            "amount": Decimal(str(amount)),
            "eta_days": Decimal(str(eta_days)),
            "status": "PENDING"
        }
        try:
            # Atomic update to append to the list
            ticket_table.update_item(
                Key={"ticketId": ticket_id},
                UpdateExpression="SET bids = list_append(if_not_exists(bids, :empty_list), :new_bid)",
                ExpressionAttributeValues={
                    ":empty_list": [],
                    ":new_bid": [new_bid]
                },
                ReturnValues="UPDATED_NEW"
            )
        except Exception as e:
            return [types.TextContent(type="text", text=json.dumps({"error": str(e)}))]
            
        return [types.TextContent(type="text", text=json.dumps({"success": True, "bid_id": bid_id}))]

    elif name == "get_ticket_context":
        ticket_id = arguments.get("ticket_id")
        caller_store_id = arguments.get("caller_store_id")
        table = dynamodb.Table("Tickets")
        response = table.get_item(Key={"ticketId": ticket_id})
        ticket = response.get("Item", {})
        
        if not ticket:
            return [types.TextContent(type="text", text=json.dumps({"error": f"Ticket {ticket_id} not found"}))]
            
        # Multi-Tenant Validation
        if caller_store_id and ticket.get("storeId") and ticket.get("storeId") != caller_store_id:
            return [types.TextContent(type="text", text=json.dumps({"error": "Unauthorized access to ticket from another store"}))]
            
        # Sort bids by 'Best Value' => low cost + low wait time penalty (50 per day)
        bids = ticket.get("bids", [])
        if bids:
            ticket["bids"] = sorted(bids, key=lambda b: float(b.get("amount", 0)) + float(b.get("eta_days", 0)) * 50)
        
        # Pull history for the same store by scanning (naive)
        store_id = ticket.get("storeId")
        history = []
        if store_id:
            try:
                history_response = table.scan(
                    FilterExpression=boto3.dynamodb.conditions.Attr("storeId").eq(store_id)
                )
                history = [t for t in history_response.get("Items", []) if t.get("ticketId") != ticket_id]
            except Exception:
                pass
        
        context = {
            "ticket": ticket,
            "ai_estimates": {
                "estimatedCost": float(ticket.get("aiEstimatedCost", 0.0)),
                "diagnosis": ticket.get("aiDiagnosis", "")
            },
            "store_history": history
        }
        return [types.TextContent(type="text", text=json.dumps(context, cls=DecimalEncoder))]

    elif name == "update_status":
        ticket_id = arguments.get("ticket_id")
        new_status = arguments.get("new_status")
        caller_store_id = arguments.get("caller_store_id")
        table = dynamodb.Table("Tickets")
        
        # Multi-Tenant Validation
        if caller_store_id:
            ticket = table.get_item(Key={"ticketId": ticket_id}).get("Item", {})
            if ticket and ticket.get("storeId") and ticket.get("storeId") != caller_store_id:
                return [types.TextContent(type="text", text=json.dumps({"error": "Unauthorized access to ticket from another store"}))]
        
        try:
            table.update_item(
                Key={"ticketId": ticket_id},
                UpdateExpression="set #status = :s",
                ExpressionAttributeNames={"#status": "status"},
                ExpressionAttributeValues={":s": new_status}
            )
            return [types.TextContent(type="text", text=json.dumps({"success": True, "ticket_id": ticket_id, "new_status": new_status}))]
        except Exception as e:
            return [types.TextContent(type="text", text=json.dumps({"error": str(e)}))]

    else:
        raise ValueError(f"Unknown tool: {name}")

def create_mcp_app():
    from fastapi import FastAPI
    from mcp.server.sse import SseServerTransport
    from starlette.requests import Request
    from starlette.responses import StreamingResponse

    app = FastAPI(title="CstoreStudio MCP Server")
    
    # SSE Transport endpoint mapped underneath
    sse = SseServerTransport("/mcp/messages")

    @app.get("/sse")
    async def handle_sse(request: Request):
        async with sse.connect_sse(
            request.scope, request.receive, request._send
        ) as streams:
            await mcp.run(
                streams[0], streams[1], mcp.create_initialization_options()
            )
            
    @app.post("/messages")
    async def handle_messages(request: Request):
        await sse.handle_post_message(request.scope, request.receive, request._send)
        
    return app
