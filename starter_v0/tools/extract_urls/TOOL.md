---
name: extract_urls
track: bonus
kind: local_formatter
requires_env: []
inputs: [text]
outputs: [urls, count]
side_effect: false
---
# extract_urls

Extracts HTTP and HTTPS links from supplied text, trims trailing punctuation, and removes
duplicate links while preserving the first-seen order. It makes no network requests.
