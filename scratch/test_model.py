import os

import litellm
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GROQ_API_KEY")

for model in ["groq/llama-3.3-70b-versatile", "groq/llama3-8b-8192", "groq/qwen/qwen3.8-27b"]:
    try:
        res = litellm.completion(
            model=model,
            messages=[{"role": "user", "content": "Hello"}],
            api_key=api_key,
        )
        print(f"SUCCESS model '{model}': {res.choices[0].message.content[:50]}")
    except Exception as e:
        print(f"FAILED model '{model}': {e}")
