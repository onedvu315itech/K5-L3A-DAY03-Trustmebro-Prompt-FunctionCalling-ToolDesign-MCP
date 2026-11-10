from __future__ import annotations

import re
from typing import Any
from urllib.parse import urlsplit


_URL_PATTERN = re.compile(r"https?://[^\s<>\"'`]+", re.IGNORECASE)
_TRAILING_PUNCTUATION = ".,;:!?)]}"


def _error(error_type: str, message: str) -> dict[str, Any]:
    return {"tool": "extract_urls", "error": error_type, "message": message}


def extract_urls(text: str = "") -> dict[str, Any]:
    """Extract HTTP(S) URLs, remove trailing punctuation, and deduplicate in order."""
    if not isinstance(text, str):
        return _error("TypeError", "text must be a string")
    if not text.strip():
        return _error("ValueError", "text must not be empty")

    urls: list[str] = []
    seen: set[str] = set()
    for match in _URL_PATTERN.findall(text):
        url = match.rstrip(_TRAILING_PUNCTUATION)
        parsed = urlsplit(url)
        if not parsed.scheme or not parsed.netloc:
            continue

        # Hosts are case-insensitive and a trailing slash does not create a
        # separate result for this simple extraction/deduplication tool.
        normalized = url.casefold().rstrip("/")
        if normalized in seen:
            continue
        seen.add(normalized)
        urls.append(url)

    return {"tool": "extract_urls", "urls": urls, "count": len(urls)}
