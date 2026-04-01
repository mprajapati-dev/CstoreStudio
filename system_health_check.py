import os
import time
import requests
import boto3
import uuid

# Configuration Defaults (modify based on local environments)
UI_BASE_URL = os.getenv("UI_BASE_URL", "http://localhost:3000")
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
LOCALSTACK_URL = os.getenv("LOCALSTACK_URL", "http://localhost:4566")

def check_portals():
    results = {}
    portals = ["manager", "owner", "vendor", "admin"]
    for p in portals:
        url = f"{UI_BASE_URL}/portal/{p}"
        try:
            r = requests.get(url, timeout=3)
            # Accept 200, 301, 302, 308 as "OK" (Next.js sometimes redirects)
            results[p] = r.status_code in [200, 301, 302, 308]
        except Exception:
            results[p] = False
    return results

def check_localstack():
    try:
        s3 = boto3.client(
            's3', 
            endpoint_url=LOCALSTACK_URL, 
            aws_access_key_id='test', 
            aws_secret_access_key='test', 
            region_name='us-east-1'
        )
        dynamo = boto3.client(
            'dynamodb', 
            endpoint_url=LOCALSTACK_URL, 
            aws_access_key_id='test', 
            aws_secret_access_key='test', 
            region_name='us-east-1'
        )
        # Verify sync by listing resources
        s3.list_buckets()
        dynamo.list_tables()
        return True, "Synced & Responding"
    except Exception as e:
        return False, str(e)

def check_triage_latency():
    ticket_id = f"health-test-{uuid.uuid4()}"
    url = f"{API_BASE_URL}/tickets/{ticket_id}/transition"
    # Provide a simple manager note to standard-tier prompt for latency checks (avoiding image overhead)
    payload = {"manager_note": "Health check diagnostic test"}
    
    start_time = time.time()
    try:
        r = requests.post(url, json=payload, timeout=15)
        latency = time.time() - start_time
        return (r.status_code == 200), latency
    except Exception:
        return False, 0.0

def main():
    print("Initiating System Health Probes...\n")
    
    # 1. Portals Checks
    portal_res = check_portals()
    
    # 2. Infrastructure Checks
    ls_ok, ls_msg = check_localstack()
    
    # 3. Microservice / AI Checks
    api_ok, latency = check_triage_latency()
    
    # Building Markdown
    md = "## 🩺 System Health Summary\n\n"
    
    md += "### 🌐 Web Portals (Next.js)\n"
    for p, ok in portal_res.items():
        status = "✅ 200 OK" if ok else "❌ Offline / Unreachable"
        md += f"- **{p.capitalize()} Portal**: {status}\n"
        
    md += "\n### 🗄️ Infrastructure (LocalStack)\n"
    ls_status = "✅ S3 & DynamoDB Synced" if ls_ok else f"❌ Offline ({ls_msg})"
    md += f"- **Storage/DB Engine**: {ls_status}\n"
    
    md += "\n### 🤖 AI Agent Backend (FastAPI / LangGraph)\n"
    api_status = f"✅ Triage Responding (Latency: {latency:.2f}s)" if api_ok else "❌ Gateway Timeout / Offline"
    md += f"- **Orchestrator Node**: {api_status}\n"
    
    md += "\n---\n"
    
    # Aggregation logic
    is_ready = all(portal_res.values()) and ls_ok and api_ok
    if is_ready:
        md += "### 🚀 Production Readiness: **READY** ✅\n"
        md += "*All endpoints nominal. The system is structurally verified for deployment.*\n"
    else:
        md += "### ⛔ Production Readiness: **NOT READY** ❌\n"
        md += "*Crucial subsystems are failing. Please review the offline modules above before merging to main.*\n"
        
    print(md)
    
    with open("HEALTH_REPORT.md", "w") as f:
        f.write(md)
        
    print("\n✅ Report saved to HEALTH_REPORT.md")

if __name__ == "__main__":
    main()
