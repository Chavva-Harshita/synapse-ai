from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PromptTemplate:
    template: str

    def render(self, *, question: str, context: str) -> str:
        return self.template.format(question=question, context=context)


# Grounding-first prompt for the Ollama model.
# Hallucination prevention requirement:
# If the answer is not in context, say you do not know.
GROUNDING_PROMPT = PromptTemplate(
    template=(
        "You are a helpful assistant. Answer the USER QUESTION using ONLY the provided CONTEXT.\n"
        "If the answer is not in context, say you do not know.\n"
        "\n"
        "CONTEXT:\n"
        "{context}\n"
        "\n"
        "USER QUESTION:\n"
        "{question}\n"
        "\n"
        "Answer (grounded in context only):"
    )
)

