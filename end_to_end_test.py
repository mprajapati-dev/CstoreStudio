import requests
import json
import time

BASE_URL = "http://localhost:8000"

def run_test():
    print("🚀 Starting End-to-End Ticket Workflow Test...")
    
    # 1. Create a ticket
    print("\n1️⃣ Creating a new ticket (Intake)...")
    triage_payload = {
        "media_url": "test.jpg",
        "category": "Plumbing",
        "manager_note": "Pipe is leaking near the register.",
        "store_id": "Store-101",
        "asset_id": "Pipe-1"
    }
    res = requests.post(f"{BASE_URL}/triage", json=triage_payload)
    if res.status_code != 200:
        print(f"❌ Failed to create ticket: {res.text}")
        return
    triage_data = res.json()
    job_id = triage_data.get("job_id")
    print(f"✅ Ticket created! Job ID: {job_id}")
    print(f"   Status: {triage_data.get('status')}")
    print(f"   Est Cost: ${triage_data.get('cost_estimate')}")
    print(f"   DIY?: {triage_data.get('is_diy')}")

    # 2. Get Jobs and Verify
    print("import requests
import json
import time

BASE_URL = "http://loca rimport json
im{Bimport timob
BASE_URL  re
def run_test():
    print("🚀 nt(    print("?     
    # 1. Create a ticket
    print("\n1️⃣ Creating )
    j    print("\n1️⃣ Crjo    triage_payload = {
        "media_url": "test.jpg",          "media_url": b_        "category": "Plumbing",          "manager_note": "Pipe {j        "store_id": "Store-101",
        "asset_id": "Pipe-1 R        "asset_id": "Pipe-1"
  \n    }
    res = requests.poos    n     if res.status_code != 200:
        print(f"❌ Failed to creai-        print(f"❌ Failed toco        return
    triage_data = res.json()
    job_id =.t    triage_da      job_id = triage_data.gejs    print(f"✅ Ticket created! Job Ipl    print(f"   Status: {triage_data.get('status') U    print(f"   Est Cost: ${triage_data.get('cost_espr    print(f"   DIY?: {triage_data.get('is_diy')}")

    # 2. te
    # 2. Get Jobs and Verify
    print("import r re    print("import requests
L}import json
import time

atimport tim
 
BASE_URL staim{Bimport timob
BASE_URL  re
def r? BASE_URL  re
deaidef run_tesex    print("?t    # 1. Create a ticket
    print("\n t    print("\n1️⃣ Cr'"    j    print("\n1️⃣ Crjoin        "media_url": "test.jpg",          "media_urca        "asset_id": "Pipe-1 R        "asset_id": "Pipe-1"
  \n    }
    res = requests.poos    n     if res.status_code != 200:
        print(f"❌ Faile_i  \n    }
    res = requests.poos    n     if res.statuval    res )         print(f"❌ Failed to creai-        print(f"❌ Faie    triage_data = res.json()
    job_id =.t    triage_da      job_id = triage_dae:    job_id =.t    triage_da_s
    # 2. te
    # 2. Get Jobs and Verify
    print("import r re    print("import requests
L}import json
import time

atimport tim
 
BASE_URL staim{Bimport timob
BASE_URL  re
def r? BASE_URL  re
deaidef run_tesex    print("?t    #  python3 /Users/mprajapati/CstoreStudio/end_to_end_test.py
 EOF
 \x03
 grep -n "@app" /Users/mprajapati/CstoreStudio/services/ai-agent/main.py
 exit
 sleep 3 && python3 /Users/mprajapati/CstoreStudio/end_to_end_test.py
 python3 /Users/mprajapati/CstoreStudio/end_to_end_test.py
 python3 -m venv /Users/mprajapati/CstoreStudio/venv && source /Users/mprajapati/CstoreStudio/venv/bin/activate && pip install requests && python3 /Users/mprajapati/CstoreStudio/end_to_end_test.py
 exit 0
 sleep 10 && cat /Users/mprajapati/CstoreStudio/end_to_end_test.py
 python3 -m venv venv && source venv/bin/activate && pip install requests && python3 end_to_end_test.py
 exit
 cat /Users/mprajapati/CstoreStudio/end_to_end_test.py
 source /Users/mprajapati/CstoreStudio/venv/bin/activate && /Users/mprajapati/CstoreStudio/venv/bin/python3 /Users/mprajapati/CstoreStudio/end_to_end_test.py > /Users/mprajapati/CstoreStudio/test_output.txt
 cat /Users/mprajapati/CstoreStudio/services/ui-app/src/app/page.tsx | head -n 40
 exit
 cat /Users/mprajapati/CstoreStudio/services/ui-app/src/app/page.tsx
 exit
 EOF
 \x04
 echo 'EOF'
 "EOF"
 'EOF'
 EOF
 ls -la /Users/mprajapati/CstoreStudio/services/ui-app/src/app/portal
 python -c "import urllib.request, json; req = urllib.request.Request('http://localhost:8000/login', method='POST', headers={'Content-Type':'application/json'}, data=json.dumps({'username':'vendor1','password':'vendor1'}).encode('utf-8')); print(urllib.request.urlopen(req).read().decode('utf-8'))"
 python /Users/mprajapati/CstoreStudio/services/ai-agent/test_login.py
 grep -nr "docker-library" /Users/mprajapati/CstoreStudio
 python /Users/mprajapati/CstoreStudio/end_to_end_test.py
 grep -rnw "services/ui-app/src" -e "via.placeholder.com"
 python -c "import urllib.request; print('logo.png' in urllib.request.urlopen('http://localhost:8000/jobs').read().decode('utf-8'))"
 python /Users/mprajapati/CstoreStudio/clean_db_logos.py
 python /Users/mprajapati/CstoreStudio/services/ai-agent/test_login.py
 python /Users/mprajapati/CstoreStudio/test_all_logins.py
 grep -rn "estimated_cost" /Users/mprajapati/CstoreStudio/services/ai-agent/main.py
 docker restart cstorestudio-ai-agent-1
 cat services/ui-app/src/app/page.tsx | grep -B 5 -A 25 "if (!res.ok)"
 python /Users/mprajapati/CstoreStudio/create_users.py
 docker-compose ps
 docker-compose ps
 grep -A 20 "/login" /Users/mprajapati/CstoreStudio/services/ai-agent/main.py
 grep -A 20 "def login" /Users/mprajapati/CstoreStudio/services/ai-agent/main.py
 python -c "import requests; print(requests.post('http://localhost:8000/login', json={'username': 'vendor1', 'password': 'password'}).json())"
 cat /Users/mprajapati/CstoreStudio/services/ai-agent/main.py | grep -i "router.post.*login" -A 10
 grep -rn "login" /Users/mprajapati/CstoreStudio/services/ai-agent/
 docker ps -a
 sh -c "docker ps -a"
 docker ps > /tmp/dockerps.txt; cat /tmp/dockerps.txt
 python -c "
import urllib.request
import json
req = urllib.request.Request('http://localhost:8000/login', method='POST', headers={'Content-Type':'application/json'}, data=json.dumps({'username':'vendor1','password':'password'}).encode('utf-8'))
with urllib.request.urlopen(req) as response:
    print(response.read().decode())" > /tmp/login_test.log; cat /tmp/login_test.log
 echo "import urllib.request\nimport json\nimport sys\n\ntry:\n    req = urllib.request.Request('http://localhost:8000/login', method='POST', headers={'Content-Type':'application/json'}, data=json.dumps({'username':'vendor1','password':'vendor1'}).encode('utf-8'))\n    with urllib.request.urlopen(req) as response:\n        print(response.read().decode())\nexcept Exception as e:\n    print(e)\n" > test_login.py && python test_login.py
 cat /Users/mprajapati/CstoreStudio/docker-compose.yml | grep -A 10 ui-app
 python -c "import subprocess; print(subprocess.check_output(['docker-compose', 'ps'], cwd='/Users/mprajapati/CstoreStudio').decode())"
 python /Users/mprajapati/CstoreStudio/test_login_all.py
 python /Users/mprajapati/CstoreStudio/test_login_all.py > /Users/mprajapati/CstoreStudio/login_all_output.txt
 docker exec cstorestudio-ui-app-1 cat /app/src/hooks/useAuth.ts
 npm run lint
 cat /Users/mprajapati/CstoreStudio/services/ui-app/.dockerignore || echo "No dockerignore"
 ls -la /Users/mprajapati/CstoreStudio/services/ui-app/.dockerignore
 cat /Users/mprajapati/CstoreStudio/services/ui-app/src/app/page.tsx | head -n 25
 docker ps
 grep -rn "estimated_cost" /Users/mprajapati/CstoreStudio/services/ui-app/src/app/portal/
 grep -rn "\.toFixed" /Users/mprajapati/CstoreStudio/services/ui-app/src
 sh -c "grep -rn '\.toFixed' /Users/mprajapati/CstoreStudio/services/ui-app/src"
 bash -c "find /Users/mprajapati/CstoreStudio/services/ui-app/src -type f | xargs grep toFixed"
 ls -lah /Users/mprajapati/CstoreStudio/services/ui-app/src/app/portal/vendor
 cat /Users/mprajapati/CstoreStudio/services/ui-app/src/app/portal/owner/page.tsx | grep "\$" -A 2 -B 2
 bash -c "cat /Users/mprajapati/CstoreStudio/services/ui-app/src/app/portal/owner/page.tsx | grep 'estimated_cost'"
 cat > /tmp/grep_script.py << 'EOF'
import os

def check_files(start_path):
    for root, dirs, files in os.walk(start_path):
        for file in files:
            if file.endswith('.tsx') or file.endswith('.ts'):
                try:
                    with open(os.path.join(root, file), 'r') as f:
                        lines = f.readlines()
                        for i, line in enumerate(lines):
                            if 'estimated_cost' in line or 'invoice_amount' in line or 'toFixed' in line or 'job.ai_diagnosis' in line:
                                print(f"{os.path.join(root, file)}:{i+1}: {line.strip()}")
                except:
                    pass

check_files('/Users/mprajapati/CstoreStudio/services/ui-app/src')
