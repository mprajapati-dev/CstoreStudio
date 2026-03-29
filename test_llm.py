import litellm
import os
os.environ["OLLAMA_API_BASE"] = "http://host.docker.internal:11434"
print("starting...")
response = litellm.completion(
    model="ollama/llava",
    messages=[{"role": "user", "content": "Hello!"}]
)
print("done!")
print(response.choices[0].message.content)
