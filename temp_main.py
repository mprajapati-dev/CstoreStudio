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
    # All tasks go straight to "Pending Bid Selection" for vendor bidding
    state["approval_status"] = "Pending Bid Selection"
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
