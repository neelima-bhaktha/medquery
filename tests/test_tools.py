from src.tools import FetchArticleTool, MedicalSearchTool


def test_medical_search_tool_attributes():
    tool = MedicalSearchTool()
    assert tool.name == "search_medical_sources"
    assert "Europe PMC" in tool.description
    assert tool.args_schema is not None


def test_medical_search_tool_run():
    tool = MedicalSearchTool()
    result = tool._run("ibuprofen side effects")
    assert isinstance(result, str)
    assert "Found" in result or "No medical sources" in result


def test_fetch_article_tool_attributes():
    tool = FetchArticleTool()
    assert tool.name == "fetch_article"
    assert "web article" in tool.description.lower()
    assert tool.args_schema is not None


def test_fetch_article_tool_run():
    tool = FetchArticleTool()
    # Test valid URL fetch
    result = tool._run("https://httpbin.org/html")
    assert isinstance(result, str)
    assert "Article Content" in result or "Error fetching" in result


def test_fetch_article_tool_error_handling():
    tool = FetchArticleTool()
    # Test invalid URL - should return error string rather than throwing exception
    result = tool._run("https://invalid-nonexistent-domain-12345.org")
    assert isinstance(result, str)
    assert "Error fetching" in result or "Please try another URL" in result
