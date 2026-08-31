from src.tools import FetchArticleTool, MedicalSearchTool


def test_medical_search_tool_attributes():
    tool = MedicalSearchTool()
    assert tool.name == "search_medical_sources"
    assert "Europe PMC" in tool.description


def test_medical_search_tool_run():
    tool = MedicalSearchTool()
    result = tool._run("ibuprofen dosage")
    assert isinstance(result, str)
    assert "Found" in result or "No medical sources found" in result


def test_fetch_article_tool_attributes():
    tool = FetchArticleTool()
    assert tool.name == "fetch_article"
    assert "extracts the main clean text" in tool.description


def test_fetch_article_tool_run():
    tool = FetchArticleTool()
    # Test whitelisted URL fetch
    result = tool._run("https://europepmc.org")
    assert isinstance(result, str)
    assert "Article Content" in result or "Unable to fetch" in result


def test_fetch_article_tool_untrusted_domain_block():
    tool = FetchArticleTool()
    # Test untrusted URL - should return domain block message rather than throwing exception
    result = tool._run("https://untrusted-blog-site-9999.com/post")
    assert isinstance(result, str)
    assert "Unable to fetch article" in result
    assert "trusted medical domain whitelist" in result
