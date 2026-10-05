from __future__ import annotations

from typing import Any

import requests # type: ignore

from app.core.config import settings


class OllamaError(RuntimeError):
    pass


class OllamaUnavailableError(OllamaError):
    pass


class OllamaModelNotFoundError(OllamaError):
    pass


def configured_model_is_available(*, timeout_s: float = 3.0) -> bool:
    """Return whether the configured Ollama model is listed by the local service."""
    model_name = settings.ollama_model
    if not model_name:
        return False

    try:
        response = requests.get(
            f"{settings.ollama_host}/api/tags",
            timeout=timeout_s,
        )
        if response.status_code != 200:
            return False
        payload = response.json()
        models = payload.get("models", []) if isinstance(payload, dict) else []
    except (requests.RequestException, ValueError, AttributeError, TypeError):
        return False
    if not isinstance(models, list):
        return False

    names = {
        name
        for item in models
        if isinstance(item, dict)
        for name in (item.get("name"), item.get("model"))
        if isinstance(name, str)
    }
    return model_name in names or (
        ":" not in model_name and f"{model_name}:latest" in names
    )


def generate_with_ollama(
    *,
    prompt: str,
    model: str | None = None,
    host: str | None = None,
    options: dict[str, Any] | None = None,
    timeout_s: float = 120.0,
) -> str:
    """Generate text using Ollama's /api/generate endpoint."""

    model_name = model or settings.ollama_model
    if not model_name:
        raise OllamaUnavailableError(
            "OLLAMA_MODEL is empty. Configure it with an installed Ollama model."
        )

    base_url = (host or settings.ollama_host).rstrip("/")
    url = f"{base_url.rstrip('/')}/api/generate"

    payload: dict[str, Any] = {
        "model": model_name,
        "prompt": prompt,
        "stream": False,
    }
    if options:
        payload["options"] = options

    try:
        resp = requests.post(url, json=payload, timeout=timeout_s)
    except requests.RequestException as e:
        raise OllamaUnavailableError(
            "Could not connect to Ollama. Verify OLLAMA_HOST and that Ollama is running."
        ) from e

    if resp.status_code != 200:
        if resp.status_code == 404:
            raise OllamaModelNotFoundError(
                f"Ollama model '{model_name}' is unavailable. Pull it with Ollama or set OLLAMA_MODEL."
            )
        raise OllamaUnavailableError(
            f"Ollama returned HTTP {resp.status_code} while generating a response."
        )

    try:
        data = resp.json()
    except ValueError as exc:
        raise OllamaUnavailableError("Ollama returned an invalid response.") from exc

    text = data.get("response")
    if not isinstance(text, str) or not text.strip():
        raise OllamaUnavailableError("Ollama returned an empty response.")

    return text.strip()
