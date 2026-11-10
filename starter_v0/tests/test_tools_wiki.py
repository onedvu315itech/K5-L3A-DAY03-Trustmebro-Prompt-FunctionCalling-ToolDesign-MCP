from __future__ import annotations

from conftest import FakeResponse
from tools import TOOL_FUNCTIONS


wiki_tool = TOOL_FUNCTIONS["wiki"]


def test_wiki_happy_path_requests_summary_and_maps_item(fake_http) -> None:
    calls = fake_http(FakeResponse({
        "title": "OpenAI",
        "description": "AI research organization",
        "extract": "OpenAI   is an\nAI research lab.",
        "content_urls": {"desktop": {"page": "https://en.wikipedia.org/wiki/OpenAI"}},
    }))

    result = wiki_tool(title="OpenAI", lang="en")

    assert calls[0]["url"] == "https://en.wikipedia.org/api/rest_v1/page/summary/OpenAI"
    assert calls[0]["headers"]["Accept"] == "application/json"
    assert result["items"][0] == {
        "title": "OpenAI",
        "url": "https://en.wikipedia.org/wiki/OpenAI",
        "source": "en.wikipedia.org",
        "summary": "OpenAI is an AI research lab.",
        "description": "AI research organization",
    }


def test_wiki_empty_title_returns_error_without_request(fake_http) -> None:
    calls = fake_http(FakeResponse({}))

    result = wiki_tool(title="   ")

    assert result["error"] == "ValueError"
    assert calls == []


def test_wiki_http_failure_returns_error_dict(fake_http) -> None:
    fake_http(FakeResponse(status_code=500))

    result = wiki_tool(title="OpenAI")

    assert result["error"] == "HTTPError"


def test_wiki_unknown_language_falls_back_and_encodes_title(fake_http) -> None:
    calls = fake_http(FakeResponse({"title": "AC/DC", "extract": "A band."}))

    result = wiki_tool(title="AC/DC band", lang="not a lang!")

    assert calls[0]["url"] == "https://en.wikipedia.org/api/rest_v1/page/summary/AC%2FDC_band"
    assert result["lang"] == "en"


def test_wiki_missing_article_returns_empty_items(fake_http) -> None:
    fake_http(FakeResponse(status_code=404))

    result = wiki_tool(title="No such exact article", lang="vi")

    assert result["items"] == []
    assert "error" not in result
    assert result["lang"] == "vi"


def test_wiki_truncates_long_summary(fake_http) -> None:
    fake_http(FakeResponse({"title": "T", "extract": "y" * 5000}))

    result = wiki_tool(title="T")

    assert len(result["items"][0]["summary"]) == 1500
    assert result["items"][0]["summary"].endswith("...")
