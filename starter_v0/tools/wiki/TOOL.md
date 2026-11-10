---
name: wiki
track: bonus
kind: live_api
provider: Wikipedia REST API
requires_env: []
inputs: [title, lang]
outputs: [items, message]
side_effect: false
---
# wiki

Fetches the summary of one Wikipedia article by title. No API key is required. The result uses
the `items` shape used by `lookup` and `fetch`, so it can be passed to `format`.

- Use for definitions and background information about a concept, person, or organization.
- Do not use for current news (`lookup`), social posts (`timeline` or `social_search`), or a specific URL (`fetch`).
- A missing exact article title returns `items=[]` and a message, not an error.
- `lang` is a two- or three-letter Wikipedia language code; invalid values fall back to `en`.
