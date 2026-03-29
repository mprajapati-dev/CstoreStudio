import os
import json
import litellm
from typing import TypedDict, Optional, List, Any
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langfuse.decorators import observe

litellm.success_callback = ["langfuse"]

class GraphState(TypedDict):
    ticket_id: str
    status: str
    media_url: Optional[str]
    manager_note: Optional[str]
    ai_diagnosis: Optional[str]
    ai_estimated_cost: float
    vendor_bid: float
    audit_flag: Optional[str]
    action: Optional[str]

@observe(name="triage_agent", as_type="generation")
def triage_agent(state: GraphState):
    media_url = state.get("media_url")
    manager_note = state.get("manager_note", "")
    
    if media_url:
        try:
            prompt = (
                f"You are an expert AI Triage agent for a C-store maintenance platform. "
                f"Analyze the submitted media and the manager's note: '{manager_note}'. "
                f"Identify the fault and estimate the repair cost in USD. "
                f"Return ONLY valid JSON with keys: 'diagnosis' (string) and 'estimated_cost' (number)."
            )
            response = litellm.completion(
                model="gemini/gemini-3.1-pro",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {"type": "image_url", "image_url": {"url": media_url}}
                        ]
                    }
                ],
                api_key=os.getenv("GEMINI_API_KEY", "dummy"),
                metadata={"ticket_id": state.get("ticket_id")}
            )
            resp_str = response.choices[0].message.content
            if "```json" in resp_str:
                resp_str = resp_str.split("```json")[1].split("```")[0].strip()
            elif "```" in resp_str:
                resp_str = resp_str.split("```")[1].strip()
            
            data = json.loads(resp_str)
            state["ai_diagnosis"] = data.get("diagnosis", "Unknown fault")
            state["ai_estimated_cost"] = float(data.get("estimated_cost", 0.0))
        except Exception as e:
            state["ai_diagnosis"] = "Fallback generic diagnosis due to vision error"
            state["ai_estimated_cost"] = 200.0
            
    state["status"] = "AWAITING_BIDS"
    return state

@observe(name="auditor_agent", as_type="generation")
def auditor_agent(state: GraphState):
    ai_cost = state.get("ai_estimated_cost", 0.0)
    vendor_bid = state.get("vendor_bid", 0.0)
    
    if ai_cost > 0 and vendor_bid > 0:
        delta = abs(vendor_bid - ai_cost) / ai_cost
        prompt = (
            f"You are an Auditor Agent. The AI estimate was ${ai_cost} and vendor bid is ${vendor_bid}. "
            f"Determine if the bid is too high (delta > 25%). If so, flag as HIGH_RISK_REASONING_REQUIRED, else OK."
        )
        response = litellm.completion(
            model="gemini/gemini-3.1-pro",
            messages=[{"role": "user", "content": prompt}],
            api_key=os.getenv("GEMINI_API_KEY", "dummy"),
            metadata={"ticket_id": state.get("ticket_id")}
        )
        if delta > 0.25:
            state["audit_flag"] = "HIGH_RISK_REASONING_REQUIRED"
        else:
            state["audit_flag"] = "OK"
            
    state["status"] = "PENDING_APPROVAL"
    return state

def owner_approval_step(state: GraphState):
    if state.get("action") == "APPROVE" or state.get("status") == "PENDING_APPROVAL":
        state["status"] = "IN_PROGRESS"
    return state

@observe(name="visual_validation", as_type="generation")
def manager_validation_step(state: GraphState):
    # Auditor's Visual Verification Logic
    media_url = state.get("media_url")
    
    if state.get("action") == "SUBMIT_FIX" or state.get("status") == "PENDING_VALIDATION":
        try:
            prompt = (
                "You are an Auditor Agent. Review the provided image of the completed repair. "
                "Return ONLY valid JSON with keys: 'verified' (boolean) and 'confidence' (number between 0.0 and 1.0)."
            )
            messages = [
                {
                    "role": "user",
                    "content": [{"type": "text", "text": prompt}]
                }
            ]
            if media_url:
                messages[0]["content"].append({"type": "image_url", "image_url": {"url": media_url}})

            response = litellm.completion(
                model="gemini/gemini-3.1-pro",
                messages=messages,
                api_key=os.getenv("GEMINI_API_KEY", "dummy"),
                metadata={"ticket_id": state.get("ticket_id")}
            )
            
            resp_str = response.choices[0].message.content
            if "```json" in resp_str:
                resp_str = resp_str.split("```json")[1].split("```")[0].strip()
            elif "```" in resp_str:
                resp_str = resp_str.split("```")[1].strip()
            
            data = json.loads(resp_str)
            verified = data.get("verified", False)
            confidence = data.get("confidence", 0.0)
            
            if verified and confidence >= 0.5:
                state["status"] = "AWAITING_PAYMENT"
            else:
                state["status"] = "VALIDATION_FAILED"
                state["audit_flag"] = "MANAGER_NOTIFICATION_TRIGGERED"
                
        except Exception as e:
            print(f"Visual Verification Failed: {e}")
            state["status"] = "VALIDATION_FAILED"
            state["audit_flag"] = "MANAGER_NOTIFICATION_TRIGGERED"

    return state

def close_ticket(state: GraphState):
    state["status"] = "CLOSED"
    return state

def supervisor_router(state: GraphState):
    status = state.get("status", "OPEN")
    
    if status == "OPEN":
        return "triage"
    elif status == "AWAITING_BIDS":
        if state.get("vendor_bid", 0) > 0:
            return "auditor"
        return END
    elif status == "PENDING_APPROVAL":
        return "owner_approval"
    elif status == "IN_PROGRESS":
        if state.get("action") == "SUBMIT_FIX":
            state["status"] = "PENDING_VALIDATION"
            return "supervisor"
        return END
    elif status == "PENDING_VALIDATION":
        return "manager_validation"
    elif status == "VALIDATION_FAILED":
        return END
    elif status == "AWAITING_PAYMENT":
        if state.get("action") == "DISPATCH_PAYMENT":
            return "close"
        return END
    elif status == "CLOSED":
        return END
        
    return END

# Build Graph
builder = StateGraph(GraphState)

builder.add_node("supervisor", lambda state: state)
builder.add_node("triage", triage_agent)
builder.add_node("auditor", auditor_agent)
builder.add_node("owner_approval", owner_approval_step)
builder.add_node("manager_validation", manager_validation_step)
builder.add_node("close", close_ticket)

builder.add_edge(START, "supervisor")
builder.add_edge("triage", "supervisor")
builder.add_edge("auditor", "supervisor")
builder.add_edge("owner_approval", "supervisor")
builder.add_edge("manager_validation", "supervisor")
builder.add_edge("close", "supervisor")

builder.add_conditional_edges(
    "supervisor",
    supervisor_router,
    {
        "triage": "triage",
        "auditor": "auditor",
        "owner_approval": "owner_approval",
        "manager_validation": "manager_validation",
        "close": "close",
        "supervisor": "supervisor",
        END: END
    }
)

memory = MemorySaver()
app_graph = builder.compile(
    checkpointer=memory,
    interrupt_before=["owner_approval"]
)
