from __future__ import annotations

from typing import Any


def similarity_search_chunks(query: str, *, top_k: int = 3, persist_dir: str | None = None):
    """Return similarity search results from persistent Chroma.

    The returned items are langchain Document objects.
    """
    from app.services.vector_store import VectorStoreManager

    manager = VectorStoreManager(persist_dir=persist_dir)
    vector_store = manager.build_or_load()

    # similarity_search returns Documents. Some vectorstores can also provide scores
    # via similarity_search_with_score; we try it first.
    try:
        docs_with_scores = vector_store.similarity_search_with_score(query, k=top_k)
        return [
            {
                "doc": d,
                "score": float(score) if score is not None else None,
            }
            for d, score in docs_with_scores
        ]
    except Exception:
        docs = vector_store.similarity_search(query, k=top_k)
        return [
            {
                "doc": d,
                "score": None,
            }
            for d in docs
        ]

