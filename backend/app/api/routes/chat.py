from typing import List, Optional

from fastapi import APIRouter, HTTPException # type: ignore
from pydantic import BaseModel # type: ignore

router = APIRouter(tags=["chat"])


class ChatRequest(BaseModel):
    message: str
    document_ids: Optional[List[str]] = None


class ChatResponse(BaseModel):
    reply: str
    retrieved_chunks: list[dict]


@router.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest) -> ChatResponse:
    """Grounded chat using local Ollama via retrieved Chroma context.

    Grounding requirement:
    - Ollama is instructed: "If answer is not in context, say you do not know." (see prompt template).
    """

    try:
        from app.services.ollama_client import generate_with_ollama
        from app.services.prompt_templates import GROUNDING_PROMPT
        from app.services.retriever import similarity_search_chunks
        from app.services.response_generation import build_retrieved_context

        # Retrieve top-k chunks from persistent Chroma.
        # NOTE: `document_ids` is currently not enforced by the retriever implementation.
        hits = similarity_search_chunks(req.message, top_k=5)

        retrieved_chunks: list[dict] = []
        for h in hits:
            doc = h.get("doc")
            if doc is None:
                continue

            retrieved_chunks.append(
                {
                    "source_text": doc.page_content,
                    "metadata": dict(doc.metadata or {}),
                    "similarity": h.get("score"),
                }
            )

        context = build_retrieved_context(retrieved_chunks)
        prompt = GROUNDING_PROMPT.render(question=req.message, context=context)

        reply = generate_with_ollama(prompt=prompt, model="llama3")

        return ChatResponse(reply=reply, retrieved_chunks=retrieved_chunks)

    except Exception as e:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=f"Chat generation failed: {e}")

