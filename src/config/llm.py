import os

from crewai import LLM
from dotenv import load_dotenv

from src.config.settings import DEFAULT_MODEL, DEFAULT_TEMPERATURE

# Ensure .env environment variables are loaded
load_dotenv()


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
    )
