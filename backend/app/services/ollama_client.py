from __future__ import annotations

import os
from typing import Any

import requests # type: ignore


class OllamaError(RuntimeError):
    pass


def generate_with_ollama(
    *,
    prompt: str,
    model: str = "qwen2.5-coder:1.5b",
    host: str | None = None,
    options: dict[str, Any] | None = None,
    timeout_s: float = 120.0,
) -> str:
    """Generate text using Ollama's /api/generate endpoint."""

    base_url = host or os.getenv("OLLAMA_HOST", "http://localhost:11434")
    url = f"{base_url.rstrip('/')}/api/generate"

    payload: dict[str, Any] = {
        "model": model,
        "prompt": prompt,
        "stream": False,
    }
    if options:
        payload["options"] = options

    try:
        resp = requests.post(url, json=payload, timeout=timeout_s)
    except requests.RequestException as e:
        raise OllamaError(f"Failed to reach Ollama at {url}: {e}") from e

    if resp.status_code != 200:
        detail = resp.text.strip()[:1000]
        raise OllamaError(
            f"Ollama error (HTTP {resp.status_code}) at {url}. Body: {detail}"
        )

    try:
        data = resp.json()
    except ValueError as e:
        raise OllamaError(f"Ollama returned non-JSON response: {resp.text[:1000]}") from e

    text = data.get("response")
    if not isinstance(text, str) or not text.strip():
        raise OllamaError(f"Ollama returned empty response payload: {data}")

    return text.strip()

