import os
import uuid
import boto3
import base64
import httpx
import json
import random
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import TypedDict, Optional
from langgraph.graph import StateGraph, END
import litellm
import time
from prometheus_client import make_asgi_app, Summary, Counter

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Prometheus metrics
triage_latency = Summary('triage_latency_seconds', 'Time spent in visual triage')
token_usage = Counter('token_usage_total', 'Tokens used by LLMs', ['model'])

app.mount("/metrics", make_asgi_app())

AWS_ENDPOINT_URL = os.getenv("AWS_ENDPOINT_URL", "http://localstack:4566")
REGION = os.getenv("AWS_DEFAULT_REGION", "us-east-1")

dynamodb = boto3.client(
    'dynamodb',
    endpoint_url=AWS_ENDPOINT_URL,
    region_name=REGION,
    aws_access_key_id='test',
    aws_secret_access_key='test'
)

class JobState(TypedDict):
    job_id: str
    media_url: str
    triage_result: str
    approval_status: str
    is_diy: bool
    estimated_cost: int
    category: str
    clerk_note: str
    bids: str
    store_id: str
    asset_id: str

# In Phase 1 we stub out complex visual AI triage in favor of routing category rules 
@triage_latency.time()
def visual_triage(state: JobState):
    print("STARTING visual_triage (Phase 1 Routing)")
    
    clerk_note = state.get('clerk_note', '')
    category = state.get('category', 'General')
    
    # In Phase 1 we just store what the clerk reported into our database.
    # We will let the "Super Agent" or dispatch rule handle the next step.
    state["triage_result"] = f"Reported issue: {clerk_note}"
    state["is_diy"] = False
    state["estimated_cost"] = 150 
        
    return state

def business_logic(state: JobState):
    print("STARTING business_logic")
    # All tasks go straight to "Draft" for Clerk Review
    state["approval_status"] = "Draft"
    return state

def generate_bids(state: JobState):
    print("STARTING generate_bids")
    category = state.get('category', 'General')
    
    vendor_names = {
        'HVAC': ['Cool Breeze HVAC', 'Arctic Air', 'HeatWave Solutions'],
        'Plumbing': ['Mario Bros Plumbing', 'Pipe Masters', 'Leak Busters'],
        'Electrical': ['Sparky Electric', 'Volts & Watts', 'Current Solutions'],
        'Fuel Tank': ['Tank Tech', 'Fuel Safe Pros', 'Pump Masters'],
        'Inventory / Coolers': ['Chill Zone', 'Frosty Coolers', 'Ice Age Repairs'],
        'General': ['Handy Dan', 'FixIt All', 'Rapid Repairs']
    }
    
    names = vendor_names.get(category, vendor_names['General'])
    bids = []
    base_cost = random.randint(100, 500)
    for i in range(3):
        amount = base_cost + random.randint(-50, 50)
        time_to_fix = random.choice(["Today", "Tomorrow", "Next Week", "In 2 Days"])
        bids.append({
            "vendor_id": f"v{i+1}",
            "vendor_name": random.choice(names),
            "amount": amount,
            "availability": time_to_fix
        })
        
    state["bids"] = json.dumps(bids)
    return state

def persistence(state: JobState):
    print("STARTING persistence")
    try:
        dynamodb.put_item(
            TableName='Jobs',
            Item={
                'jobId': {'S': state['job_id']},
                'mediaUrl': {'S': state.get('media_url', '')},
                'triageResult': {'S': state.get('triage_result', '')},
                'approvalStatus': {'S': state.get('approval_status', '')},
                'isDiy': {'BOOL': state.get('is_diy', False)},
                'estimatedCost': {'N': str(state.get('estimated_cost', 0))},
                'category': {'S': state.get('category', 'General')},
                'bids': {'S': state.get('bids', '[]')},
                'clerkNote': {'S': state.get('clerk_note', '')},
                'storeId': {'S': state.get('store_id', '')},
                'assetId': {'S': state.get('asset_id', '')}
            }
        )
        print("dynamodb put_item finished.")
    except Exception as e:
        print(f"DynamoDB Error: {e}")
    return state

workflow = StateGraph(JobState)
workflow.add_node("visual_triage", visual_triage)
workflow.add_node("business_logic", business_logic)
workflow.add_node("generate_bids", generate_bids)
workflow.add_node("persistence", persistence)

workflow.set_entry_point("visual_triage")
workflow.add_edge("visual_triage", "business_logic")
workflow.add_edge("business_logic", "persistence")
workflow.add_edge("persistence", END)

app_graph = workflow.compile()

class TriageRequest(BaseModel):
    media_url: str
    category: str
    clerk_note: str
    store_id: str
    asset_id: str

@app.post("/triage")
async def start_triage(request: TriageRequest):
    job_id = str(uuid.uuid4())
    inputs = JobState(
        job_id=job_id, 
        media_url=request.media_url, 
        triage_result="", 
        approval_status="", 
        is_diy=False, 
        estimated_cost=0,
        category=request.category,
        clerk_note=request.clerk_note,
        bids="[]",
        store_id=request.store_id,
        asset_id=request.asset_id
    )
    try:
        result = app_graph.invoke(inputs)
        return {
            "job_id": job_id, 
            "status": result["approval_status"], 
            "details": result["triage_result"],
            "cost_estimate": result["estimated_cost"],
            "is_diy": result["is_diy"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"ERROR: {str(e)} type: {type(e)}")

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/jobs")
def get_jobs():
    try:
        response = dynamodb.scan(TableName='Jobs')
        jobs = []
        for item in response.get('Items', []):
            jobs.append({
                "job_id": item.get("jobId", {}).get("S", ""),
                "media_url": item.get("mediaUrl", {}).get("S", ""),
                "triage_result": item.get("triageResult", {}).get("S", ""),
                "approval_status": item.get("approvalStatus", {}).get("S", ""),
                "is_diy": item.get("isDiy", {}).get("BOOL", False),
                "estimated_cost": int(item.get("estimatedCost", {}).get("N", "0")),
                "qa_notes": item.get("qaNotes", {}).get("S", ""),
                "ai_diagnosis": item.get("aiDiagnosis", {}).get("S", ""),
                "post_repair_media_url": item.get("postRepairMediaUrl", {}).get("S", ""),
                "clerk_note": item.get("clerkNote", {}).get("S", ""),
                "vendor_notes": item.get("vendorNotes", {}).get("S", ""),
                "store_id": item.get("storeId", {}).get("S", ""),
                "asset_id": item.get("assetId", {}).get("S", ""),
                "invoice_amount": float(item.get("invoiceAmount", {}).get("N", "0")),
                "category": item.get("category", {}).get("S", "General"),
                "bids": item.get("bids", {}).get("S", "[]")
            })
        return {"jobs": jobs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"ERROR: {str(e)} type: {type(e)}")

class JobUpdate(BaseModel):
    status: Optional[str] = None
    vendor_notes: Optional[str] = None
    invoice_amount: Optional[float] = None
    post_repair_media_url: Optional[str] = None
    bids: Optional[str] = None
    qa_notes: Optional[str] = None

@app.put("/jobs/{job_id}")
def update_job_status(job_id: str, update: JobUpdate):
    try:
        update_expr_parts = []
        expr_vals = {}
        
        if update.status is not None:
            update_expr_parts.append('approvalStatus = :val')
            expr_vals[':val'] = {'S': update.status}
        
        if update.vendor_notes is not None:
            update_expr_parts.append('vendorNotes = :vn')
            expr_vals[':vn'] = {'S': update.vendor_notes}
            
        if update.invoice_amount is not None:
            update_expr_parts.append('invoiceAmount = :ia')
            expr_vals[':ia'] = {'N': str(update.invoice_amount)}
            
        if update.post_repair_media_url is not None:
            update_expr_parts.append('postRepairMediaUrl = :pru')
            expr_vals[':pru'] = {'S': update.post_repair_media_url}
            
        if update.bids is not None:
            update_expr_parts.append('bids = :bids')
            expr_vals[':bids'] = {'S': update.bids}
            
        if update.qa_notes is not None:
            update_expr_parts.append('qaNotes = :qa')
            expr_vals[':qa'] = {'S': update.qa_notes}

        if not update_expr_parts:
            return {"status": "ok"}
            
        update_expr = "SET " + ", ".join(update_expr_parts)

        dynamodb.update_item(
            TableName='Jobs',
            Key={'jobId': {'S': job_id}},
            UpdateExpression=update_expr,
            ExpressionAttributeValues=expr_vals
        )
        return {"job_id": job_id, "status": update.status}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"ERROR: {str(e)} type: {type(e)}")

class VerifyRequest(BaseModel):
    post_repair_media_url: str

@app.post("/jobs/{job_id}/verify")
async def verify_repair(job_id: str, request: VerifyRequest):
    try:
        # Get original job context
        resp = dynamodb.get_item(TableName='Jobs', Key={'jobId': {'S': job_id}})
        item = resp.get('Item')
        if not item:
            raise HTTPException(status_code=404, detail="Job not found")

        original_issue = item.get("triageResult", {}).get("S", "Unknown issue")
        
        # Download new picture
        internal_url = request.post_repair_media_url.replace("localhost", "localstack")
        img_response = httpx.get(internal_url)
        img_response.raise_for_status()
        base64_image = base64.b64encode(img_response.content).decode('utf-8')
        
        llm_model = os.getenv("LLM_MODEL", "ollama/llava")
        if "ollama" in llm_model:
            os.environ["OLLAMA_API_BASE"] = os.getenv("OLLAMA_API_BASE", "http://host.docker.internal:11434")

        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text", 
                        "text": f"You are an AI Quality Assurance verifier. The original maintenance issue was: '{original_issue}'. Look at this new photo of the completed repair. Is it fixed properly? Output strictly in JSON with keys: 'is_fixed' (boolean), and 'qa_notes' (string)."
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        }
                    }
                ]
            }
        ]
        
        completion_response = litellm.completion(
            model=llm_model,
            messages=messages,
            response_format={ "type": "json_object" }
        )
        
        raw_content = completion_response.choices[0].message.content
        parsed = json.loads(raw_content)
        
        is_fixed = parsed.get("is_fixed", False)
        qa_notes = parsed.get("qa_notes", str(raw_content))
        new_status = "Ready for Payment" if is_fixed else "Rework Required"
        
        # update dynamodb
        dynamodb.update_item(
            TableName='Jobs',
            Key={'jobId': {'S': job_id}},
            UpdateExpression='SET approvalStatus = :status, qaNotes = :notes, postRepairMediaUrl = :url',
            ExpressionAttributeValues={
                ':status': {'S': new_status},
                ':notes': {'S': qa_notes},
                ':url': {'S': request.post_repair_media_url}
            }
        )
        
        return {
            "job_id": job_id,
            "status": new_status,
            "is_fixed": is_fixed,
            "qa_notes": qa_notes
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"ERROR: {str(e)} type: {type(e)}")

@app.post("/jobs/{job_id}/ai-diagnose")
async def ai_diagnose(job_id: str):
    try:
        # Get original job context
        resp = dynamodb.get_item(TableName='Jobs', Key={'jobId': {'S': job_id}})
        item = resp.get('Item')
        if not item:
            raise HTTPException(status_code=404, detail="Job not found")

        media_url = item.get("mediaUrl", {}).get("S", "")
        if not media_url:
            raise HTTPException(status_code=400, detail="No media attached to diagnose")
            
        # Download picture
        internal_url = media_url.replace("localhost", "localstack")
        try:
            img_response = httpx.get(internal_url)
            img_response.raise_for_status()
            base64_image = base64.b64encode(img_response.content).decode('utf-8')
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to fetch image: {e}")
        
        llm_model = os.getenv("LLM_MODEL", "ollama/llava")
        if "ollama" in llm_model:
            os.environ["OLLAMA_API_BASE"] = os.getenv("OLLAMA_API_BASE", "http://host.docker.internal:11434")

        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text", 
                        "text": "Analyze this photo of a maintenance issue. Provide a brief technical diagnosis of the visible damage, potential cause, and suggested fix."
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        }
                    }
                ]
            }
        ]
        
        print(f"Requesting AI diagnosis using model {llm_model}...")
        completion_response = litellm.completion(
            model=llm_model,
            messages=messages
        )
        
        ai_diagnosis = completion_response.choices[0].message.content
        
        dynamodb.update_item(
            TableName='Jobs',
            Key={'jobId': {'S': job_id}},
            UpdateExpression='SET aiDiagnosis = :aiDiag',
            ExpressionAttributeValues={
                ':aiDiag': {'S': ai_diagnosis}
            }
        )
        
        return {
            "job_id": job_id,
            "ai_diagnosis": ai_diagnosis
        }

    except Exception as e:
        print(f"AI Diagnosis Error: {e}")
        raise HTTPException(status_code=500, detail=f"ERROR: {str(e)} type: {type(e)}")
