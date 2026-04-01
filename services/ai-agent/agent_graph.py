import os
import json
import litellm
from typing import TypedDict, Optional, List, Any
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
# from langfuse.decorators import observe

litellm.success_callback = ["langfuse"]

class GraphState(TypedDict):
    ticket_id: str
    status: str
    tier: Optional[str]
    free_vision_credits: Optional[int]
    credits_consumed: Optional[int]
    media_url: Optional[str]
    initial_media_url: Optional[str]
    manager_note: Optional[str]
    ai_diagnosis: Optional[str]
    ai_estimated_cost: float
    vendor_bid: float
    audit_flag: Optional[str]
    auditor_reasoning: Optional[str]
    action: Optional[str]

# @observe(name="triage_agent", as_type="generation")
def triage_agent(state: GraphState):
    # Skip AI diagnosis if manual diagnosis is already provided
    if state.get("ai_diagnosis") and state.get("ai_estimated_cost", 0) > 0:
        state["status"] = "PENDING_APPROVAL"
    state["action"] = None
    return state

    media_url = state.get("media_url")
    manager_note = state.get("manager_note", "")
    tier = state.get("tier", "STANDARD")
    credits = state.get("free_vision_credits", 0)
    
    # User manually triggered vision by hitting the button (passing action=USE_VISION_CREDIT)
    # or they uploaded an image while having premium/credits available on first open.
    wants_vision = True if media_url else False
    
    can_use_vision = (tier == "PREMIUM") or (tier == "STANDARD" and credits > 0)
    
    try:
        if wants_vision and can_use_vision:
            # Consume 1 credit if they are on standard tier
            if tier == "STANDARD":
                state["credits_consumed"] = 1
                
            prompt = (
                f"You are an expert AI Triage agent for a C-store maintenance platform. "
                f"Analyze the submitted media and the manager's note: '{manager_note}'. "
                f"Identify the fault and estimate the repair cost in USD. "
                f"Return ONLY valid JSON with keys: 'diagnosis' (string) and 'estimated_cost' (number)."
            )
            messages = [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": media_url}}
                    ]
                }
            ]
            model_name = "gemini/gemini-3.1-pro" # Expensive Vision model
        else:
            # Standard Tier: Text only, saves API limits and costs
            prompt = (
                f"You are an expert AI Triage agent for a C-store maintenance platform. "
                f"Based ONLY on the manager's note: '{manager_note}', "
                f"identify the fault and estimate the repair cost in USD. "
                f"Return ONLY valid JSON with keys: 'diagnosis' (string) and 'estimated_cost' (number)."
            )
            messages = [{"role": "user", "content": [{"type": "text", "text": prompt}]}]
            model_name = "gemini/gemini-3.1-pro" # Or replace with a cheap model like 'gpt-4o-mini'
            
        response = litellm.completion(
            model=model_name,
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
        state["ai_diagnosis"] = data.get("diagnosis", "Unknown fault")
        state["ai_estimated_cost"] = float(data.get("estimated_cost", 0.0))
    except Exception as e:
        state["ai_diagnosis"] = f"Fallback generic diagnosis due to AI error: {e}"
        state["ai_estimated_cost"] = 200.0
            
    state["status"] = "PENDING_APPROVAL"
    state["action"] = None
    return state

def bid_auditor_agent(state: GraphState):
    ai_cost = state.get("ai_estimated_cost", 0.0)
    vendor_bid = state.get("vendor_bid", 0.0)
    
    # Edge case: Vendor submitted a 0 dollar bid or negative amount
    if state.get("action") == "SUBMIT_BID" and vendor_bid <= 0.0:
        state["audit_flag"] = "INVALID_BID"
        state["auditor_reasoning"] = "Vendor submitted a $0 bid. This is highly suspicious and invalid."
        state["status"] = "OPEN" # Move it back to open so managers can re-dispatch
        return state

    # If using multiple bids via Market Agent, logic could get the best bid here, 
    # but for now we evaluate the top vendor_bid attached to state.
    if ai_cost > 0 and vendor_bid > 0:
        delta = abs(vendor_bid - ai_cost) / ai_cost
        
        prompt = (
            f"You are an Auditor Agent. The AI estimate was ${ai_cost} and vendor bid is ${vendor_bid}. "
            f"Provide a brief 1-sentence reasoning comparing them."
        )
        try:
            response = litellm.completion(
                model="gemini/gemini-3.1-pro",
                messages=[{"role": "user", "content": prompt}],
                api_key=os.getenv("GEMINI_API_KEY", "dummy"),
                metadata={"ticket_id": state.get("ticket_id")}
            )
            state["auditor_reasoning"] = response.choices[0].message.content.strip()
        except:
            state["auditor_reasoning"] = f"Vendor bid is {'higher' if vendor_bid > ai_cost else 'lower'} than AI estimate by {round(delta*100)}%."

        # Safety Check: >30% over estimate
        if delta > 0.30 and vendor_bid > ai_cost:
            state["audit_flag"] = "HIGH_RISK"
        else:
            state["audit_flag"] = "OK"
            
    state["status"] = "PENDING_APPROVAL"
    state["action"] = None
    return state

def owner_approval_step(state: GraphState):
    if state.get("action") == "APPROVE":
        state["status"] = "IN_PROGRESS"
    return state

# @observe(name="visual_validation", as_type="generation")
def visual_auditor_agent(state: GraphState):
    # Auditor Agent's Visual Verification Logic
    media_url = state.get("media_url")
    initial_media_url = state.get("initial_media_url")
    
    if state.get("action") == "SUBMIT_FIX" or state.get("status") == "PENDING_VALIDATION":
        if not media_url:
            state["status"] = "VALIDATION_FAILED"
            state["manager_note"] = "No image provided for visual verification. Is the upload successful?"
            state["audit_flag"] = "MISSING_EVIDENCE"
            return state

        try:
            prompt = (
                "You are an Auditor Agent. Review the provided image(s). We are comparing the 'Fix Photo' against the 'Initial Problem Photo'. "
                "Verify that the issue is actually resolved and that the vendor didn't submit the exact same photo. "
                "Return ONLY valid JSON with keys: 'verified' (boolean), 'confidence' (number between 0.0 and 1.0), and 'reasoning' (string)."
            )
            messages = [
                {
                    "role": "user",
                    "content": [{"type": "text", "text": prompt}]
                }
            ]
            if initial_media_url:
                messages[0]["content"].append({"type": "text", "text": "Initial Problem Photo:"})
                messages[0]["content"].append({"type": "image_url", "image_url": {"url": initial_media_url}})
            
            if media_url:
                messages[0]["content"].append({"type": "text", "text": "Completion / After Photo:"})
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
            reasoning = data.get("reasoning", "")
            
            state["manager_note"] = reasoning
            
            if verified and confidence >= 0.5:
                state["action"] = None
                state["status"] = "AWAITING_PAYMENT"
            else:
                state["status"] = "VALIDATION_FAILED"
                state["audit_flag"] = "MANAGER_NOTIFICATION_TRIGGERED"
                
        except Exception as e:
            print(f"Visual Verification Failed: {e}")
            state["status"] = "VALIDATION_FAILED"
            state["audit_flag"] = "MANAGER_NOTIFICATION_TRIGGERED"

    state["action"] = None
    return state

def close_ticket(state: GraphState):
    state["status"] = "CLOSED"
    state["action"] = None
    return state

def supervisor_node(state: GraphState):
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
    return state

def supervisor_router(state: GraphState):
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

# Build Graph
builder = StateGraph(GraphState)

builder.add_node("supervisor", supervisor_node)
builder.add_node("triage", triage_agent)
builder.add_node("bid_auditor", bid_auditor_agent)
builder.add_node("owner_approval", owner_approval_step)
builder.add_node("visual_auditor", visual_auditor_agent)
builder.add_node("close", close_ticket)

builder.add_edge(START, "supervisor")
builder.add_edge("triage", "supervisor")
builder.add_edge("bid_auditor", "supervisor")
builder.add_edge("owner_approval", "supervisor")
builder.add_edge("visual_auditor", "supervisor")
builder.add_edge("close", "supervisor")

builder.add_conditional_edges(
    "supervisor",
    supervisor_router,
    {
        "triage": "triage",
        "bid_auditor": "bid_auditor",
        "owner_approval": "owner_approval",
        "visual_auditor": "visual_auditor",
        "close": "close",
        "supervisor": "supervisor",
        END: END
    }
)

memory = MemorySaver()
app_graph = builder.compile(
    checkpointer=memory
)
