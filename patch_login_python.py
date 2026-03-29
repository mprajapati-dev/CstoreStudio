import re
with open('services/ai-agent/main.py', 'r') as f:
    text = f.read()

login_model = """
class LoginRequest(BaseModel):
    username: str
    password: str

@app.post("/login")
def login(req: LoginRequest):
    try:
        resp = dynamodb.get_item(TableName='Users', Key={'username': {'S': req.username}})
        item = resp.get('Item')
        if not item:
            raise HTTPException(status_code=401, detail="Invalid username or password")
        
        stored_pass = item.get('password', {}).get('S', '')
        if stored_pass != req.password:
            raise HTTPException(status_code=401, detail="Invalid username or password")
        
        return {
            "username": item.get('username', {}).get('S'),
            "role": item.get('role', {}).get('S'),
            "permissions": item.get('permissions', {}).get('SS')
        }
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"ERROR: {str(e)}")

class TriageRequest(BaseModel):
"""

text = text.replace("class TriageRequest(BaseModel):", login_model)

with open('services/ai-agent/main.py', 'w') as f:
    f.write(text)
