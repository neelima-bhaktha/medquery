from src.core.whitelist import can_fetch, get_domain, is_trusted_domain


def test_get_domain():
    assert get_domain("https://medlineplus.gov/article/123.html") == "medlineplus.gov"
    assert get_domain("https://api.fda.gov/drug/label.json") == "api.fda.gov"


def test_is_trusted_domain():
    assert is_trusted_domain("https://medlineplus.gov/topic.html") is True
    assert is_trusted_domain("https://labels.fda.gov/drug.html") is True
    assert is_trusted_domain("https://unknown-random-blog-site.com/post") is False


def test_can_fetch_robots():
    # MedlinePlus allows general indexing
    assert can_fetch("https://medlineplus.gov/") is True
    # Invalid URL returns False
    assert can_fetch("not-a-valid-url") is False
