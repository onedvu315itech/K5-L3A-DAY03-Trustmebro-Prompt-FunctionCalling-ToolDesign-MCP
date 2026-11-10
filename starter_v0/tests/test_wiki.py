from __future__ import annotations

from conftest import FakeResponse
from tools import TOOL_FUNCTIONS


wiki_tool = TOOL_FUNCTIONS["wiki"]


# 1. Happy path ----------------------------------------------------

def test_wiki_returns_article_summary(fake_http):
    response_data = {
        "title": "Python",
        "description": "Programming language",
        "extract": "Python is a high-level programming language.",
        "content_urls": {
            "desktop": {
                "page": "https://en.wikipedia.org/wiki/Python"
            }
        }
    }

    calls = fake_http(FakeResponse(response_data))

    result = wiki_tool(title="Python", lang="en")

    # Kiểm tra request gửi đi
    assert len(calls) == 1
    assert calls[0]["method"] == "GET"
    assert calls[0]["url"] == (
        "https://en.wikipedia.org/api/rest_v1/page/summary/Python"
    )
    assert calls[0]["headers"]["Accept"] == "application/json"

    # Kiểm tra kết quả trả về
    assert result["tool"] == "wiki_summary"
    assert result["title"] == "Python"
    assert result["lang"] == "en"

    assert result["items"][0] == {
        "title": "Python",
        "url": "https://en.wikipedia.org/wiki/Python",
        "source": "en.wikipedia.org",
        "summary": "Python is a high-level programming language.",
        "description": "Programming language",
    }


# 2. Invalid input -------------------------------------------------

def test_wiki_empty_title_returns_error_without_request(fake_http):
    calls = fake_http(FakeResponse({}))

    result = wiki_tool(title="")

    assert calls == []
    assert result["error"] == "ValueError"
    assert "title must be a non-empty string" in result["message"]


def test_wiki_invalid_language_falls_back_to_english(fake_http):
    calls = fake_http(FakeResponse({
        "title": "Python",
        "extract": "Python summary",
        "content_urls": {
            "desktop": {
                "page": "https://en.wikipedia.org/wiki/Python"
            }
        }
    }))

    result = wiki_tool(title="Python", lang="12345")

    assert len(calls) == 1
    assert calls[0]["url"] == (
        "https://en.wikipedia.org/api/rest_v1/page/summary/Python"
    )
    assert result["lang"] == "en"


# 3. Article not found ---------------------------------------------

def test_wiki_article_not_found_returns_empty_items(fake_http):
    calls = fake_http(FakeResponse(status_code=404))

    result = wiki_tool(title="NonExistingArticle")

    assert len(calls) == 1
    assert result["items"] == []
    assert result["title"] == "NonExistingArticle"
    assert "No Wikipedia article" in result["message"]


# 4. HTTP error ----------------------------------------------------

def test_wiki_http_error_returns_error_dict(fake_http):
    calls = fake_http(FakeResponse(status_code=429))

    result = wiki_tool(title="Python")

    assert len(calls) == 1
    assert result["error"] == "HTTPError"
    assert "HTTP 429" in result["message"]