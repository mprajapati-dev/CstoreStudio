import os
import base64
import litellm
import json

target_model = "gemini/gemini-2.0-flash" 

def test_cloud_vision():
    print(f"Testing litellm with Model: {target_model}")
    pixel_gif = b'R0lGODlhAQABAIAAAP///wAAACH5BAEAAAAALAAAAAABAAEAAAICRAEAOw=='
    b64_img = base64.b64encode(pixel_gif).decode('utf-8')

    messages = [
        {
            "role": "user",
            "content": [
                {
                    "type": "text", 
                    "text": "Analyze this convenience store maintenance issue. Format exactly as JSON keys: 'description' (string), 'is_diy' (boolean), and 'estimated_cost' (integer)."
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/gif;base64,{b64_img}"
                    }
                }
            ]
        }
    ]

    try:
        response = litellm.completion(
            model=target_model,
            messages=messages,
            response_format={ "type": "json_object" }
        )
        print("\n✅ SUCCESS! Cloud Model Responded:\n")
        print(json.dumps(response.choices[0].message.content, indent=2))
        
    except litellm.RateLimitError as e:
        print("\n❌ RATE LIMIT ERROR.")
        print(str(e))
    except Exception as e:
        print(f"\n❌ UNKNOWN ERROR: {e}")

if __name__ == "__main__":
    test_cloud_vision()