import os
import time
import requests
from dotenv import load_dotenv

load_dotenv()

model = os.getenv("MODEL_NAME", "qwen3:14b")
host = os.getenv("OLLAMA_HOST", "http://localhost:11434")

prompt = """
You are a Unity programmer.
Write a short implementation plan for:
Player presses E to interact with nearby object.
Keep it under 10 bullet points.
"""

start = time.time()

response = requests.post(
    f"{host}/api/generate",
    json={
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.2,
            "num_ctx": 8192,
        },
    },
    timeout=180,
)

elapsed = time.time() - start
response.raise_for_status()
data = response.json()

text = data.get("response", "")
eval_count = data.get("eval_count")
eval_duration = data.get("eval_duration")

print(text.strip())
print("\n--- Benchmark ---")
print(f"Elapsed seconds: {elapsed:.2f}")

if eval_count and eval_duration:
    tokens_per_sec = eval_count / (eval_duration / 1_000_000_000)
    print(f"Output tokens: {eval_count}")
    print(f"Tokens/sec: {tokens_per_sec:.2f}")