import urllib.request
import json
import sys

def test_login(username, password):
    req = urllib.request.Request('http://localhost:8000/login', method='POST', headers={'Content-Type':'application/json'}, data=json.dumps({'username':username,'password':password}).encode('utf-8'))
    try:
        with urllib.request.urlopen(req) as response:
            print(f"{username}: {response.read().decode()}")
    except Exception as e:
        print(f"{username}: Error - {e}")

test_login('owner', 'owner')
test_login('vendor1', 'vendor1')
test_login('admin', 'admin')
test_login('manager', 'manager')
