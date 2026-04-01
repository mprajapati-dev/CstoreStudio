import re

with open("services/ai-agent/agent_graph.py", "r") as f:
    code = f.read()

# Clear action at the end of visual_auditor_agent
code = re.sub(
    r'(state\["audit_flag"\] = "MANAGER_NOTIFICATION_TRIGGERED"\n\n\s*return state)',
    'state["audit_flag"] = "MANAGER_NOTIFICATION_TRIGGERED"\n\n    state["action"] = None\n    return state',
    code
)

code = re.sub(
    r'(state\["status"\] = "AWAITING_PAYMENT"\n\s*else:\n\s*state\["status"\] = "VALIDATION_FAILED")',
    'state["action"] = None\n            state["status"] = "AWAITING_PAYMENT"\n            else:\n                state["status"] = "VALIDATION_FAILED"',
    code
)

# And clear action in close_ticket
code = re.sub(
    r'def close_ticket\(state: GraphState\):\n\s*state\["status"\] = "CLOSED"\n\s*return state',
    'def close_ticket(state: GraphState):\n    state["status"] = "CLOSED"\n    state["action"] = None\n    return state',
    code
)

# And clear action in triage
code = re.sub(
    r'(state\["status"\] = "PENDING_APPROVAL"\n\s*return state)',
    'state["status"] = "PENDING_APPROVAL"\n    state["action"] = None\n    return state',
    code
)

# Also clear it during IN_PROGRESS set in supervisor_node if action is DISPATCH, wait, supervisor_node shouldn't clear it because supervisor_router needs it!
# But for DISPATCH supervisor_router returns END immediately, so the loop stops!

with open("services/ai-agent/agent_graph.py", "w") as f:
    f.write(code)

print("Nodes patched to clear action.")
