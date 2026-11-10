from __future__ import annotations

from tools import TOOL_FUNCTIONS


extract_urls = TOOL_FUNCTIONS["extract_urls"]


def test_extract_urls_deduplicates_and_preserves_first_seen_order() -> None:
    result = extract_urls(
        "Read https://example.com/a, then https://example.org/b. "
        "Again https://example.com/a."
    )

    assert result == {
        "tool": "extract_urls",
        "urls": ["https://example.com/a", "https://example.org/b"],
        "count": 2,
    }


def test_extract_urls_with_no_links_returns_empty_list() -> None:
    result = extract_urls("This paragraph has no links.")

    assert result["urls"] == []
    assert result["count"] == 0


def test_extract_urls_wrong_type_returns_error_dict() -> None:
    result = extract_urls(text=42)

    assert result["error"] == "TypeError"
    assert result["message"] == "text must be a string"
