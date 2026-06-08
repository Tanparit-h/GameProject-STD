import os
import requests
from dotenv import load_dotenv

load_dotenv()

model = os.getenv("MODEL_NAME", "qwen3:14b")
host = os.getenv("OLLAMA_HOST", "http://localhost:11434")

response = requests.post(
    f"{host}/api/generate",
    json={
        "model": model,
        "prompt": "Reply with only: PYTHON_OLLAMA_OK",
        "stream": False,
    },
    timeout=120,
)

response.raise_for_status()
data = response.json()

print(data.get("response", "").strip())