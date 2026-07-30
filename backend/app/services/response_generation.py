from __future__ import annotations

from dataclasses import dataclass

from app.services.ollama_client import generate_with_ollama
from app.services.prompt_templates import GROUNDING_PROMPT


@dataclass(frozen=True)
class GenerationResult:
    reply: str


def build_retrieved_context(chunks: list[dict]) -> str:
    """Convert retrieved chunks into a single context string."""

    parts: list[str] = []
    for i, ch in enumerate(chunks, start=1):
        source_text = ch.get("source_text")
        if not isinstance(source_text, str) or not source_text.strip():
            continue

        parts.append(f"[Chunk {i}]\n{source_text.strip()}")

    return "\n\n".join(parts).strip()


def generate_grounded_reply(*, question: str, retrieved_chunks: list[dict], model: str = "llama3") -> GenerationResult:
    """Generate a grounded reply using Ollama and the grounding prompt."""

    context = build_retrieved_context(retrieved_chunks)
    prompt = GROUNDING_PROMPT.render(question=question, context=context or "")

    reply = generate_with_ollama(prompt=prompt, model=model)
    return GenerationResult(reply=reply)

