from __future__ import annotations

import re
from typing import Any
from urllib.parse import quote

import requests

from tools._shared import TIMEOUT, domain, err


WIKI_SUMMARY_URL = "https://{lang}.wikipedia.org/api/rest_v1/page/summary/{title}"
MAX_SUMMARY_CHARS = 1500
USER_AGENT = "AI20k-Day03-Research-Agent/1.0 (educational lab; contact: local)"


def wiki_summary(title: str = "", lang: str = "en") -> dict[str, Any]:
    """Return one Wikipedia article summary in the same item shape as lookup/fetch."""
    try:
        clean_title = " ".join(str(title or "").split())
        if not clean_title:
            raise ValueError("title must be a non-empty string")

        language = str(lang or "en").strip().lower()
        if not re.fullmatch(r"[a-z]{2,3}", language):
            language = "en"

        encoded_title = quote(clean_title.replace(" ", "_"), safe="")
        url = WIKI_SUMMARY_URL.format(lang=language, title=encoded_title)
        response = requests.get(
            url,
            headers={"User-Agent": USER_AGENT, "Accept": "application/json"},
            timeout=TIMEOUT,
        )
        if response.status_code == 404:
            return {
                "tool": "wiki_summary",
                "title": clean_title,
                "lang": language,
                "items": [],
                "message": "No Wikipedia article with this exact title.",
            }
        response.raise_for_status()

        data = response.json()
        page_url = ((data.get("content_urls") or {}).get("desktop") or {}).get("page") or ""
        extract = " ".join(str(data.get("extract") or "").split())
        if len(extract) > MAX_SUMMARY_CHARS:
            extract = extract[: MAX_SUMMARY_CHARS - 3] + "..."
        return {
            "tool": "wiki_summary",
            "title": clean_title,
            "lang": language,
            "items": [{
                "title": data.get("title") or clean_title,
                "url": page_url,
                "source": domain(page_url) or f"{language}.wikipedia.org",
                "summary": extract,
                "description": data.get("description") or "",
            }],
        }
    except Exception as exc:
        return err("wiki_summary", exc)
