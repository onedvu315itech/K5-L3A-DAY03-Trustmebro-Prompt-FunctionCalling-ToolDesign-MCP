from __future__ import annotations

import json
import os
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from providers.base import ModelResponse, ToolCall


class DeployApiProvider:
    """OpenRouter provider routed through the separately deployed API service."""

    default_model = "openai/gpt-4o-mini"

    def __init__(self, *, version: str) -> None:
        self.version = version
        self.endpoint = os.getenv("DEPLOY_API_URL", "http://localhost:3000/api/complete")

    def complete(
        self,
        messages: list[dict[str, str]],
        tools: list[dict[str, Any]] | None = None,
        *,
        model: str | None = None,
        temperature: float = 0.0,
        tool_choice: Any | None = None,
    ) -> ModelResponse:
        payload: dict[str, Any] = {
            "provider": "openrouter",
            "version": self.version,
            "messages": messages,
            "temperature": temperature,
        }
        if model:
            payload["model"] = model
        if tools:
            payload["tools"] = tools
        if tool_choice is not None:
            payload["tool_choice"] = tool_choice

        request = Request(
            self.endpoint,
            data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
            headers={"Content-Type": "application/json", "Accept": "application/json"},
            method="POST",
        )
        try:
            with urlopen(request, timeout=75) as response:
                result = json.loads(response.read().decode("utf-8"))
        except HTTPError as exc:
            details = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"Deploy API returned HTTP {exc.code}: {details}") from exc
        except URLError as exc:
            raise RuntimeError(f"Could not reach deploy API at {self.endpoint}: {exc.reason}") from exc
        except (TimeoutError, OSError) as exc:
            raise RuntimeError(f"Deploy API request failed at {self.endpoint}: {exc}") from exc

        if not isinstance(result, dict):
            raise RuntimeError("Deploy API returned a non-object response.")
        calls: list[ToolCall] = []
        for call in result.get("tool_calls", []):
            if isinstance(call, dict) and isinstance(call.get("name"), str):
                args = call.get("args", {})
                calls.append(ToolCall(name=call["name"], args=args if isinstance(args, dict) else {}))
        return ModelResponse(text=result.get("text"), tool_calls=calls, raw=result)
