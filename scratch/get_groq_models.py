import os
import json
import urllib.request
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GROQ_API_KEY")

headers = {
    "Authorization": f"Bearer {api_key}",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}
req = urllib.request.Request("https://api.groq.com/openai/v1/models", headers=headers)
try:
    with urllib.request.urlopen(req) as res:
        data = json.loads(res.read().decode())
        models = [m["id"] for m in data.get("data", [])]
        print("ACTIVE GROQ MODELS:", models)
except Exception as e:
    print("FAILED TO FETCH MODELS:", e)
