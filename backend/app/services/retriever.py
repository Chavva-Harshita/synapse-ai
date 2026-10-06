from __future__ import annotations

from app.services.vector_store import VectorStoreManager, VectorStoreUnavailableError

# The small evaluation had overlapping supported (0.295-1.198) and unsupported
# (0.553-1.668) distances; this remains an initial heuristic, not a universal cutoff.
MAX_CHROMA_DISTANCE = 0.7


class DocumentNotIndexedError(RuntimeError):
    pass


def similarity_search_chunks(
    query: str,
    *,
    top_k: int = 3,
    document_id: str | None = None,
    persist_dir: str | None = None,
):
    """Return similarity search results from persistent Chroma.

    The returned items are langchain Document objects.
    """
    manager = VectorStoreManager(persist_dir=persist_dir)
    vector_store = manager.build_or_load(create_if_missing=False)

    metadata_filter = {"document_id": document_id} if document_id is not None else None
    try:
        if metadata_filter is not None:
            indexed = vector_store.get(
                where=metadata_filter,
                limit=1,
                include=["metadatas"],
            )
            if not indexed.get("ids"):
                raise DocumentNotIndexedError(
                    "The requested document has no indexed chunks."
                )

        docs_with_scores = vector_store.similarity_search_with_score(
            query,
            k=top_k,
            filter=metadata_filter,
        )
    except DocumentNotIndexedError:
        raise
    except Exception as exc:  # noqa: BLE001
        raise VectorStoreUnavailableError(
            "Chroma failed while retrieving document chunks."
        ) from exc

    return [
        {
            "doc": doc,
            "score": float(score),
        }
        for doc, score in docs_with_scores
        if score is not None and float(score) <= MAX_CHROMA_DISTANCE
    ]
