import re

with open('services/ai-agent/main.py', 'r') as f:
    code = f.read()

verify_patch = """
        original_issue = item.get("triageResult", {}).get("S", "Unknown issue")
        original_media_url = item.get("mediaUrl", {}).get("S", "")
        
        # Download new picture
        internal_url = request.post_repair_media_url.replace("localhost", "localstack")
        img_response = httpx.get(internal_url)
        img_response.raise_for_status()
        base64_image_new = base64.b64encode(img_response.content).decode('utf-8')

        # Download old picture
        base64_image_old = ""
        if original_media_url:
            try:
                old_internal = original_media_url.replace("localhost", "localstack")
                old_img_response = httpx.get(old_internal)
                old_img_response.raise_for_status()
                base64_image_old = base64.b64encode(old_img_response.content).decode('utf-8')
            except Exception as e:
                print(f"Failed to fetch old image: {e}")

        llm_model = os.getenv("LLM_MODEL", "gemini/gemini-pro-vision")
        if "ollama" in llm_model:
            os.environ["OLLAMA_API_BASE"] = os.getenv("OLLAMA_API_BASE", "http://host.docker.internal:11434")

        content_elements = [
            {
                "type": "text", 
                "text": f"You are an AI Quality Assurance verifier. The original maintenance issue was: '{original_issue}'. You will see two images (if available). The first is the AFTER photo. The second is the BEFORE photo. Compare them. Is the issue fixed properly? Output strictly in JSON with keys: 'is_fixed' (boolean), and 'qa_notes' (string)."
            },
            {
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{base64_image_new}"
                }
            }
        ]
        
        if base64_image_old:
            content_elements.append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{base64_image_old}"
                }
            })

        messages = [
            {
                "role": "user",
                "content": content_elements
            }
        ]
"""

code = re.sub(
    r'(\s+)original_issue = item\.get\("triageResult".*?messages = \[\n\s+\{\n\s+"role": "user",\n\s+"content": \[.*?\]\n\s+\}\n\s+\]',
    r'\1' + verify_patch.strip().replace('\n', '\n\1'),
    code,
    flags=re.DOTALL
)

with open('services/ai-agent/main.py', 'w') as f:
    f.write(code)
