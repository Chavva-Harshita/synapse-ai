from __future__ import annotations

import logging

from fastapi import APIRouter, HTTPException # type: ignore

from app.api.routes.retrieval_models import RetrieveRequest, RetrieveResponse, RetrievedChunk
from app.services.retriever import similarity_search_chunks
from app.services.vector_store import VectorStoreUnavailableError

router = APIRouter(tags=["retrieval"])


@router.post("/retrieve", response_model=RetrieveResponse)
def retrieve(req: RetrieveRequest):
    try:
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
    except VectorStoreUnavailableError:
        raise HTTPException(status_code=503, detail="The retrieval index is unavailable.")
    except Exception:  # noqa: BLE001
        logging.getLogger(__name__).exception("Retrieval failed")
        raise HTTPException(status_code=500, detail="Retrieval failed unexpectedly.")
