from __future__ import annotations

from typing import Optional

from app.services.text_chunker import chunk_text
from app.services.vector_store import VectorStoreManager


def embed_and_store_pdf_chunks(
    *,
    text: str,
    document: dict,
    chunk_size: int = 1000,
    chunk_overlap: int = 200,
    embedding_model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
    vector_store: Optional[VectorStoreManager] = None,
) -> dict:
    """Chunk extracted PDF text and store embeddings in persistent Chroma."""

    chunks = chunk_text(text, chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    if not chunks:
        return {
            "stored": 0,
            "chunks": [],
            "chunk_size": chunk_size,
            "chunk_overlap": chunk_overlap,
        }

    document_id = document.get("id")
    document_name = document.get("name")
    if not isinstance(document_id, str) or not document_id:
        raise ValueError("A stored document ID is required to index PDF chunks")

    metadatas = [
        {
            "document_id": document_id,
            "document_name": document_name or "",
            "chunk_index": i,
            "chunk_size": chunk_size,
            "chunk_overlap": chunk_overlap,
        }
        for i in range(len(chunks))
    ]

    manager = vector_store or VectorStoreManager()
    stored = manager.add_texts(
        texts=chunks,
        metadatas=metadatas,
        ids=[f"{document_id}:{i}" for i in range(len(chunks))],
        embedding_model_name=embedding_model_name,
    )

    return {
        "stored": stored,
        "chunks": chunks,
        "chunk_size": chunk_size,
        "chunk_overlap": chunk_overlap,
    }
