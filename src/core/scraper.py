import logging
import re
from typing import Dict, Optional

import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util import Retry

from src.core.cache import SQLiteCache
from src.core.whitelist import can_fetch, get_domain, is_trusted_domain

logger = logging.getLogger(__name__)

# Global cache instance
_cache = SQLiteCache()


def _get_session(retries: int = 3, backoff_factor: float = 0.5) -> requests.Session:
    """
    Create requests Session with Retry strategy for 2-3 retries.
    """
    session = requests.Session()
    retry_strategy = Retry(
        total=retries,
        backoff_factor=backoff_factor,
        status_forcelist=[429, 500, 502, 503, 504],
        raise_on_status=False,
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session


def clean_html_text(html: str) -> tuple[str, str]:
    """
    Parse HTML using BeautifulSoup with lxml parser.
    Removes clutter tags (script, style, nav, etc.) and returns (title, clean_text).
    """
    soup = BeautifulSoup(html, "lxml")

    # Remove script, style, navigation, headers, footers, forms
    for tag in soup(["script", "style", "nav", "header", "footer", "form", "noscript", "svg", "iframe", "aside"]):
        tag.decompose()

    # Extract page title
    title = soup.title.string.strip() if soup.title and soup.title.string else "Untitled Article"

    # Extract content text (prefer main/article tags if present)
    main_content = soup.find("main") or soup.find("article") or soup.body or soup

    # Get text lines
    text_blocks = []
    for elem in main_content.find_all(["p", "h1", "h2", "h3", "h4", "li", "span"]):
        txt = elem.get_text().strip()
        if txt and len(txt) > 20 and not txt.startswith("{"):
            text_blocks.append(txt)

    if not text_blocks:
        text_blocks = [main_content.get_text()]

    raw_text = "\n\n".join(text_blocks)
    # Clean multiple whitespace/newlines
    clean_text = re.sub(r"\n{3,}", "\n\n", raw_text)
    clean_text = re.sub(r"[ \t]+", " ", clean_text).strip()

    return title, clean_text


def scrape_article(
    url: str,
    max_chars: int = 2000,
    timeout: int = 8,
    retries: int = 3,
    use_cache: bool = True,
    user_agent: str = "MedQueryMedicalCrew/1.0",
) -> Dict[str, Optional[str]]:
    """
    Fetch and extract clean text from a web article.

    Features:
    - 1. Hard domain whitelist verification before scraping.
    - 2. Checks SQLite cache first if use_cache=True.
    - 3. Enforces robots.txt check via urllib.robotparser.
    - 4. Uses requests with configurable timeout and 2-3 retries.
    - 5. Parses with BeautifulSoup + lxml.
    - 6. Truncates text to max_chars (default 2000).
    - 7. Saves to SQLite cache for fast offline re-runs.
    """
    url_clean = url.strip()
    domain = get_domain(url_clean)

    # Step 1: Hard Domain Whitelist Verification
    if not is_trusted_domain(url_clean):
        logger.warning(f"[HARD DOMAIN BLOCK] Scraping refused for non-whitelisted domain '{domain}': {url_clean}")
        return {
            "url": url_clean,
            "title": "Domain Blocked",
            "text": f"Scraping blocked: Domain '{domain}' is not in the trusted medical domain whitelist.",
            # pyrefly: ignore [bad-assignment]
            "cached": False,
            "status": "blocked_untrusted_domain",
        }

    # Step 2: Check SQLite Cache
    if use_cache:
        cached = _cache.get(url_clean)
        if cached:
            logger.info(f"Cache hit for URL: {url_clean}")
            truncated_text = cached["text"][:max_chars]
            return {
                "url": url_clean,
                "title": cached["title"],
                "text": truncated_text,
                # pyrefly: ignore [bad-assignment]
                "cached": True,
                "status": "success",
            }

    # Step 3: Check robots.txt permissions
    if not can_fetch(url_clean, user_agent=user_agent, enforce_trusted=True):
        logger.warning(f"Robots.txt disallowed scraping for URL: {url_clean}")
        return {
            "url": url_clean,
            "title": "Access Blocked",
            "text": "Scraping disallowed by robots.txt rules.",
            # pyrefly: ignore [bad-assignment]
            "cached": False,
            "status": "blocked_by_robots",
        }

    # Step 4: Fetch web page using requests session with retry strategy
    session = _get_session(retries=retries)
    headers = {
        "User-Agent": user_agent,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    }

    try:
        response = session.get(url_clean, headers=headers, timeout=timeout)
        response.raise_for_status()

        # Step 5: Parse HTML with BeautifulSoup + lxml
        title, clean_text = clean_html_text(response.text)

        # Step 6: Truncate text to max_chars (2000 chars)
        truncated_text = clean_text[:max_chars]

        # Step 7: Store in SQLite Cache
        if use_cache:
            _cache.set(url_clean, title, clean_text)

        return {
            "url": url_clean,
            "title": title,
            "text": truncated_text,
            # pyrefly: ignore [bad-assignment]
            "cached": False,
            "status": "success",
        }

    except Exception as e:  # noqa: BLE001
        logger.error(f"Failed to scrape URL '{url_clean}': {e}")
        return {
            "url": url_clean,
            "title": "Fetch Error",
            "text": f"Error scraping article: {e}",
            # pyrefly: ignore [bad-assignment]
            "cached": False,
            "status": "error",
        }
