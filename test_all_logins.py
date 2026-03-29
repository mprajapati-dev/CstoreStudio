import urllib.request
import json

base_url = 'http://localhost:8000/login'
users = [
    ('admin', 'admin'),
    ('manager', 'manager'),
    ('owner', 'owner'),
    ('vendor1', 'vendor1')
]

for username, password in users:
    try:
        req = urllib.request.Request(
            base_url, 
            method='POST', 
            headers={'Content-Type':'application/json'}, 
            data=json.dumps({'username': username, 'password': password}).encode('utf-8')
        )
        response = urllib.request.urlopen(req)
        data = json.loads(response.read().decode('utf-8'))
        print(f"✅ Login successful for {username}. Role returned: {data.get('role')}")
    except Exception as e:
        print(f"❌ Login failed for {username}: {e}")
