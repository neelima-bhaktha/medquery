import os
import re
import time

import litellm
from crewai import LLM
from dotenv import load_dotenv

from src.config.settings import DEFAULT_MODEL, DEFAULT_TEMPERATURE

# Ensure .env environment variables are loaded
load_dotenv()

# Configure LiteLLM to drop unsupported parameters for Groq
litellm.drop_params = True

# Monkeypatch litellm.completion to remove 'cache_control'/'cache_breakpoint' and handle RateLimit retries dynamically
_original_completion = litellm.completion


def _sanitized_completion(*args, **kwargs):
    if "messages" in kwargs and isinstance(kwargs["messages"], list):
        for msg in kwargs["messages"]:
            if isinstance(msg, dict):
                msg.pop("cache_control", None)
                msg.pop("cache_breakpoint", None)

    max_retries = 2  # Fail fast after 2 retries to prevent minute-long stalls
    for attempt in range(max_retries):
        try:
            return _original_completion(*args, **kwargs)
        except litellm.exceptions.RateLimitError as e:
            err_msg = str(e)
            if attempt == max_retries - 1:
                raise e
            match = re.search(r"Please try again in (\d+(?:\.\d+)?)s", err_msg)
            sleep_time = float(match.group(1)) + 1.0 if match else 5.0
            print(
                f"[LiteLLM Wrapper] Rate limit hit (attempt {attempt + 1}/{max_retries}). "
                f"Waiting {sleep_time:.1f}s..."
            )
            time.sleep(sleep_time)


litellm.completion = _sanitized_completion


def get_llm(
    model: str = DEFAULT_MODEL,
    temperature: float = DEFAULT_TEMPERATURE,
) -> LLM:
    """
    Initialize and return configured CrewAI LLM instance.
    Reads GROQ_API_KEY from environment or .env.
    """
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        api_key = os.getenv("groq_api_key")

    return LLM(
        model=model,
        temperature=temperature,
        api_key=api_key,
        drop_params=True,
    )
