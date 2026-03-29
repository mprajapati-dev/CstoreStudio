with open('services/ai-agent/main.py', 'r') as f:
    c = f.read()

graph_old = """workflow.add_node("generate_bids", generate_bids)
workflow.add_node("persistence", persistence)

workflow.set_entry_point("visual_triage")
workflow.add_edge("visual_triage", "business_logic")
workflow.add_edge("business_logic", "persistence")
workflow.add_edge("persistence", END)"""

graph_new = """workflow.add_node("generate_bids", generate_bids)
workflow.add_node("payment_processing", payment_processing)
workflow.add_node("persistence", persistence)

workflow.set_entry_point("visual_triage")
workflow.add_edge("visual_triage", "business_logic")
# In standard triage we just do persistence. 
# Payment processing can be called separately or mocked.
workflow.add_edge("business_logic", "persistence")
workflow.add_edge("persistence", END)"""

c = c.replace(graph_old, graph_new)

with open('services/ai-agent/main.py', 'w') as f:
    f.write(c)
