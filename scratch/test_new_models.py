import os
import litellm
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GROQ_API_KEY")

for m in ["groq/openai/gpt-oss-20b", "groq/qwen/qwen3.6-27b", "groq/allam-2-7b", "groq/qwen/qwen3.8-27b"]:
    try:
        res = litellm.completion(
            model=m,
            messages=[{"role": "user", "content": "Hello"}],
            api_key=api_key,
        )
        print(f"SUCCESS: '{m}' -> {res.choices[0].message.content[:40]}")
    except Exception as e:
        print(f"FAILED: '{m}' -> {str(e)[:70]}")
