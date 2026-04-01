import re

with open("services/ai-agent/agent_graph.py", "r") as f:
    code = f.read()

# 1. Update triage_agent status return
code = re.sub(
    r'state\["status"\] = "AWAITING_BIDS"\s*return state',
    'state["status"] = "PENDING_APPROVAL"\n    return state',
    code
)

# 2. Rewrite supervisor_node
supervisor_node_replacement = '''def supervisor_node(state: GraphState):
    action = state.get("action")
    status = state.get("status", "OPEN")
    
    if action == "DISPATCH":
        state["status"] = "IN_PROGRESS"
    elif action == "CREATE":
        if state.get("targetVendorId") or state.get("selected_vendor_id"):
            state["status"] = "IN_PROGRESS"
    elif action == "VERIFY":
        state["status"] = "AWAITING_PAYMENT"
    elif action == "SUBMIT_FIX":
        state["status"] = "PENDING_VALIDATION"
    return state'''

code = re.sub(
    r'def supervisor_node\(state: GraphState\):[\s\S]*?return state',
    supervisor_node_replacement,
    code,
    count=1
)

# 3. Rewrite supervisor_router
supervisor_router_replacement = '''def supervisor_router(state: GraphState):
    status = state.get("status", "OPEN")
    action = state.get("action")

    if action == "CREATE":
        if state.get("targetVendorId") or state.get("selected_vendor_id"):
            return END
        else:
            return "triage"

    if not action or action in ["DISPATCH", "BROADCAST", "VERIFY"]:
        return END
        
    if action == "SUBMIT_FIX" or status == "PENDING_VALIDATION":
        return "visual_auditor"
    
    if action == "TRIAGE" or (status == "OPEN" and action == "SUBMIT"):
        return "triage"

    if status == "AWAITING_PAYMENT":
        if state.get("action") == "DISPATCH_PAYMENT":
            return "close"
        return END
        
    return END'''

code = re.sub(
    r'def supervisor_router\(state: GraphState\):[\s\S]*?return END',
    supervisor_router_replacement,
    code,
    count=1
)

with open("services/ai-agent/agent_graph.py", "w") as f:
    f.write(code)

print("agent_graph.py patched.")
