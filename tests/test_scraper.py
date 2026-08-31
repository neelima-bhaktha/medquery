import os

# pyrefly: ignore [missing-import]
from src.core.cache import SQLiteCache

# pyrefly: ignore [missing-import]
from src.core.scraper import clean_html_text, scrape_article


def test_clean_html_text():
    html = """
    <html>
        <head><title>Sample Medical Article Title</title></head>
        <body>
            <script>console.log("script block");</script>
            <style>body { color: red; }</style>
            <nav><a href="#">Nav link</a></nav>
            <main>
                <h1>Main Heading</h1>
                <p>This is a test paragraph for medical article text extraction using BeautifulSoup and lxml.</p>
                <p>This is a second paragraph containing relevant health info for testing HTML cleaning.</p>
            </main>
        </body>
    </html>
    """
    title, text = clean_html_text(html)
    assert title == "Sample Medical Article Title"
    assert "script block" not in text
    assert "Nav link" not in text
    assert "This is a test paragraph for medical article text" in text


def test_sqlite_cache():
    db_path = ".cache/unit_test_cache.db"
    cache = SQLiteCache(db_path=db_path)
    url = "https://example.com/test-page"

    try:
        cache.set(url, "Test Title", "Test extracted text content")
        cached = cache.get(url)
        assert cached is not None
        assert cached["title"] == "Test Title"
        assert cached["text"] == "Test extracted text content"
    finally:
        cache.clear()
        if os.path.exists(db_path):
            try:
                os.remove(db_path)
            except OSError:
                pass


def test_scrape_article_truncation_and_caching():
    test_url = "https://httpbin.org/html"
    res1 = scrape_article(test_url, max_chars=2000, use_cache=True)
    assert res1["status"] == "success"
    assert len(res1["text"]) <= 2000

    # Second call should return cached=True
    res2 = scrape_article(test_url, max_chars=2000, use_cache=True)
    assert res2["status"] == "success"
    assert res2["cached"] is True
    assert len(res2["text"]) <= 2000
