from __future__ import annotations

from fastapi import APIRouter, HTTPException # type: ignore

from app.api.routes.retrieval_models import RetrieveRequest, RetrieveResponse, RetrievedChunk
from app.services.retriever import similarity_search_chunks

router = APIRouter(tags=["retrieval"])


@router.post("/retrieve", response_model=RetrieveResponse)
def retrieve(req: RetrieveRequest):
    try:
        if req.top_k < 1:
            raise ValueError("top_k must be >= 1")

        hits = similarity_search_chunks(req.query, top_k=req.top_k)

        results: list[RetrievedChunk] = []
        for h in hits:
            doc = h["doc"]
            score = h.get("score")
            results.append(
                RetrievedChunk(
                    source_text=doc.page_content,
                    metadata=dict(doc.metadata or {}),
                    similarity=score,
                )
            )

        return RetrieveResponse(query=req.query, results=results)
    except Exception as e:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=f"Retrieval failed: {e}")

