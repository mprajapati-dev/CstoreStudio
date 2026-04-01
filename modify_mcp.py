import re

with open("services/ai-agent/mcp_server.py", "r") as f:
    content = f.read()

# Update tool schema
old_schema = """            name="post_bid",
            description="Saves a vendor bid.",
            inputSchema={
                "type": "object",
                "properties": {
                    "ticket_id": {"type": "string"},
                    "vendor_id": {"type": "string"},
                    "amount": {"type": "number"}
                },
                "required": ["ticket_id", "vendor_id", "amount"]
            }"""
new_schema = """            name="post_bid",
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
            }"""

content = content.replace(old_schema, new_schema)

old_impl = """    elif name == "post_bid":
        ticket_id = arguments.get("ticket_id")
        vendor_id = arguments.get("vendor_id")
        amount = arguments.get("amount")
        
        import uuid
        bid_id = str(uuid.uuid4())
        table = dynamodb.Table("Bids")
        table.put_item(
            Item={
                "bidId": bid_id,
                "ticketId": ticket_id,
                "vendorId": vendor_id,
                "amount": Decimal(str(amount)),
                "availability": "Immediate", # default for mock
                "status": "PENDING"
            }
        )
        return [types.TextContent(type="text", text=json.dumps({"success": True, "bid_id": bid_id}))]"""

new_impl = """    elif name == "post_bid":
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
            
        return [types.TextContent(type="text", text=json.dumps({"success": True, "bid_id": bid_id}))]"""

content = content.replace(old_impl, new_impl)

with open("services/ai-agent/mcp_server.py", "w") as f:
    f.write(content)

