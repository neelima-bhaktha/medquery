import logging
import os
import sqlite3
import time
from typing import Dict, Optional

logger = logging.getLogger(__name__)

DEFAULT_CACHE_DIR = ".cache"
DEFAULT_DB_NAME = "web_cache.db"


class SQLiteCache:
    """
    Tiny SQLite disk cache for web page scraping results, keyed by URL.
    """

    def __init__(self, db_path: Optional[str] = None):
        if db_path is None:
            os.makedirs(DEFAULT_CACHE_DIR, exist_ok=True)
            db_path = os.path.join(DEFAULT_CACHE_DIR, DEFAULT_DB_NAME)

        self.db_path = db_path
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        with self._get_connection() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS page_cache (
                    url TEXT PRIMARY KEY,
                    title TEXT,
                    text TEXT,
                    fetched_at REAL
                )
                """
            )
            conn.commit()

    def get(self, url: str) -> Optional[Dict[str, str]]:
        """
        Retrieve cached page content for a URL.
        Returns dict with keys 'title', 'text', 'fetched_at' or None if not cached.
        """
        url_normalized = url.strip()
        try:
            with self._get_connection() as conn:
                cursor = conn.execute(
                    "SELECT title, text, fetched_at FROM page_cache WHERE url = ?",
                    (url_normalized,),
                )
                row = cursor.fetchone()
                if row:
                    return {
                        "title": row["title"],
                        "text": row["text"],
                        "fetched_at": row["fetched_at"],
                    }
        except sqlite3.Error as e:
            logger.debug(f"SQLite cache fetch error for URL '{url_normalized}': {e}")
        return None

    def set(self, url: str, title: str, text: str) -> None:
        """
        Store title and scraped text for a URL in the cache.
        """
        url_normalized = url.strip()
        now = time.time()
        try:
            with self._get_connection() as conn:
                conn.execute(
                    """
                    INSERT OR REPLACE INTO page_cache (url, title, text, fetched_at)
                    VALUES (?, ?, ?, ?)
                    """,
                    (url_normalized, title, text, now),
                )
                conn.commit()
        except sqlite3.Error as e:
            logger.debug(f"SQLite cache set error for URL '{url_normalized}': {e}")

    def clear(self) -> None:
        """
        Clear all entries from the cache.
        """
        try:
            with self._get_connection() as conn:
                conn.execute("DELETE FROM page_cache")
                conn.commit()
        except sqlite3.Error as e:
            logger.debug(f"SQLite cache clear error: {e}")
