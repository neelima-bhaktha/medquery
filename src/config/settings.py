import os

# Default LLM configuration
DEFAULT_MODEL = os.getenv("LLM_MODEL", "groq/llama-3.3-70b-versatile")
DEFAULT_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.2"))

# Scraper & Search Settings
MAX_ARTICLE_CHARS = 2000
HTTP_TIMEOUT_SECONDS = 8
MAX_HTTP_RETRIES = 3

# Paths
OUTPUT_DIR = "outputs"
DEFAULT_OUTPUT_FILE = os.path.join(OUTPUT_DIR, "report.md")
