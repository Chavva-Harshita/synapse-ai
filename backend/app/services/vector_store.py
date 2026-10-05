from __future__ import annotations

import os
from functools import lru_cache
from typing import Iterable, Optional

from app.core.config import settings

EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


class VectorStoreUnavailableError(RuntimeError):
    pass


@lru_cache(maxsize=2)
def _get_embedding_function(embedding_model_name: str):
    from langchain_core.embeddings import Embeddings # type: ignore
    from langchain_huggingface import HuggingFaceEmbeddings # type: ignore

    embeddings: Embeddings = HuggingFaceEmbeddings(model_name=embedding_model_name)
    return embeddings


class VectorStoreManager:
    """Thin wrapper around LangChain Chroma persistent vector store."""

    def __init__(self, persist_dir: str | None = None) -> None:
        self.persist_dir = persist_dir or settings.chroma_dir

    def build_or_load(
        self,
        embedding_model_name: str = EMBEDDING_MODEL_NAME,
        *,
        create_if_missing: bool = False,
    ):
        if not os.path.isdir(self.persist_dir):
            if not create_if_missing:
                raise VectorStoreUnavailableError(
                    "The Chroma index has not been created yet."
                )
            os.makedirs(self.persist_dir, exist_ok=True)

        try:
            from langchain_chroma import Chroma # type: ignore

            embeddings = _get_embedding_function(embedding_model_name)
            return Chroma(
                collection_name="synapse_ai_docs",
                embedding_function=embeddings,
                persist_directory=self.persist_dir,
            )
        except Exception as exc:  # noqa: BLE001
            raise VectorStoreUnavailableError(
                "Could not open the Chroma index or initialize its embedding model."
            ) from exc

    def check_embedding_model(
        self,
        embedding_model_name: str = EMBEDDING_MODEL_NAME,
    ) -> None:
        vector = _get_embedding_function(embedding_model_name).embed_query(
            "Synapse RAG readiness check"
        )
        if not vector:
            raise VectorStoreUnavailableError("The embedding model returned no vector.")

    def add_texts(
        self,
        texts: Iterable[str], # type: ignore
        metadatas: Optional[list[dict]] = None, # type: ignore
        ids: Optional[list[str]] = None, # type: ignore
        embedding_model_name: str = EMBEDDING_MODEL_NAME,
    ) -> int:
        vector_store = self.build_or_load(
            embedding_model_name=embedding_model_name,
            create_if_missing=True,
        )

        texts_list = list(texts)

        if not texts_list:
            return 0

        if ids is None and metadatas:
            document_ids = {metadata.get("document_id") for metadata in metadatas}
            if len(document_ids) == 1 and None not in document_ids:
                document_id = next(iter(document_ids))
                ids = [f"{document_id}:{index}" for index in range(len(texts_list))]

        vector_store.add_texts(
            texts=texts_list,
            metadatas=metadatas,
            ids=ids,
        )

        return len(texts_list)