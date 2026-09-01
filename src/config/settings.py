import os

# Default LLM configuration (qwen3.6-27b is active, fast & reliable on Groq)
DEFAULT_MODEL = os.getenv("LLM_MODEL", "groq/qwen/qwen3.6-27b")
DEFAULT_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.2"))

# Scraper & Search Settings
MAX_ARTICLE_CHARS = 1200
HTTP_TIMEOUT_SECONDS = 8
MAX_HTTP_RETRIES = 3

# Paths
OUTPUT_DIR = "outputs"
DEFAULT_OUTPUT_FILE = os.path.join(OUTPUT_DIR, "report.md")
