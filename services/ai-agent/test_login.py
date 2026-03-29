import urllib.request, json
req = urllib.request.Request('http://localhost:8000/login', method='POST', headers={'Content-Type':'application/json'}, data=json.dumps({'username':'vendor1','password':'vendor1'}).encode('utf-8'))
print(urllib.request.urlopen(req).read().decode('utf-8'))
