import os
import litellm
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GROQ_API_KEY")

models_to_test = [
    "groq/qwen/qwen3.8-27b",
    "groq/qwen-2.5-32b",
    "groq/deepseek-r1-distill-qwen-32b",
    "groq/gemma2-9b-it",
    "groq/llama-3.2-3b-preview",
    "groq/llama-3.2-1b-preview",
    "groq/llama-3.3-70b-specdec",
    "groq/mixtral-8x7b-32768",
]

for m in models_to_test:
    try:
        res = litellm.completion(
            model=m,
            messages=[{"role": "user", "content": "Hi"}],
            api_key=api_key,
        )
        print(f"WORKING: '{m}' -> {res.choices[0].message.content[:40]}")
    except Exception as e:
        err = str(e)
        if "model_not_found" in err or "does not exist" in err:
            status = "MODEL NOT FOUND"
        elif "decommissioned" in err:
            status = "DECOMMISSIONED"
        elif "rate_limit_exceeded" in err:
            status = "RATE LIMITED"
        else:
            status = f"ERROR: {err[:60]}"
        print(f"FAILED: '{m}' -> {status}")
