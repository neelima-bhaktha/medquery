import logging
import os

from dotenv import load_dotenv

logger = logging.getLogger(__name__)


def validate_config(strict: bool = True) -> None:
    """
    Validate required startup environment variables.
    Fails fast on app boot if critical credentials (GROQ_API_KEY) are missing.
    """
    load_dotenv()

    api_key = os.getenv("GROQ_API_KEY") or os.getenv("groq_api_key")

    if not api_key:
        err_msg = (
            "\n"
            "=======================================================================\n"
            "CRITICAL STARTUP ERROR: Missing Environment Variable 'GROQ_API_KEY'\n"
            "-----------------------------------------------------------------------\n"
            "MedQuery requires a valid GROQ_API_KEY to run the multi-agent LLM crew.\n"
            "Please create or update your .env file with:\n"
            "    GROQ_API_KEY=your_groq_api_key_here\n"
            "or export GROQ_API_KEY in your shell environment before booting.\n"
            "=======================================================================\n"
        )
        logger.critical(err_msg)
        if strict:
            raise RuntimeError(err_msg)

    logger.info("Startup configuration validation PASSED. GROQ_API_KEY verified.")
