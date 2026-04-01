import re

with open("services/ai-agent/agent_graph.py", "r") as f:
    text = f.read()

new_funcs = '''
def supervisor_node(state: GraphState):
    action = state.get("action")
    status = state.get("status", "OPEN")
    
    # Handle direct dispatch from Manager Portal
    if action == "DISPATCH":
        state["status"] = "IN_PROGRESS"
    elif action == "BROADCAST":
        state["status"] = "AWAITING_BIDS"
    elif action == "CREATE" and state.get("ai_diagnosis") and state.get("ai_estimated_cost", 0) > 0:
        state["status"] = "AWAITING_BIDS"
    elif action == "VERIFY":
        state["status"] = "AWAITING_PAYMENT"
    elif action == "SUBMIT_FIX":
        if state.get("tier") == "PREMIUM":
            state["status"] = "PENDING_VALIDATION"
        else:
            state["status"] = "MANUAL_VALIDATION_REQUIRED"
    return state

def supervisor_router(state: GraphState):
    status = state.get("status", "OPEN")
    action = state.get("action")

    if not action or action in ["CREATE", "DISPATCH", "BROADCAST"]:
        return END
        
    if action == "VERIFY":
        return END
        
    if action == "SUBMIT_FIX":
        if status == "PENDING_VALIDATION":
            return "visual_auditor"
        return END
    
    if action == "TRIAGE" or (status == "OPEN" and action == "SUBMIT"):
        return "triage"
    elif status == "AWAITING_BIDS":
        from market_agent import check_bids
        bids = check_bids(state["ticket_id"])
        # Market Agent logic via router
        if state.get("vendor_bid", 0) > 0 or bids >= 3 or state.get("action") in ["EVALUATE_BIDS", "SUBMIT_BID"]:
            return "bid_auditor"
        return END
    elif status == "PENDING_APPROVAL":
        return "owner_approval"
    elif status == "PENDING_VALIDATION":
        return "visual_auditor"
    elif status == "VALIDATION_FAILED":
        return END
    elif status == "MANUAL_VALIDATION_REQUIRED":
        return END
    elif status == "AWAITING_PAYMENT":
        if state.get("action") == "DISPATCH_PAYMENT":
            return "close"
        return END
    elif status == "CLOSED":
        return END
        
    return END
'''

# Use regex to replace the two functions entirely
pattern = re.compile(r'def supervisor_node\(state: GraphState\):.*?return END\n\n# Build Graph', re.DOTALL)
if pattern.search(text):
    text = pattern.sub(new_funcs.strip() + '\n\n# Build Graph', text)
    with open("services/ai-agent/agent_graph.py", "w") as f:
        f.write(text)
    print("Patched successfully!")
else:
    print("Pattern not found!")
