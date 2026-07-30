from __future__ import annotations

import os
from typing import Iterable, Optional


def _default_persist_dir() -> str:
    return os.getenv("SYNAPSE_CHROMA_DIR", "./chroma_db")

class VectorStoreManager:
    """Thin wrapper around LangChain Chroma persistent vector store."""

    def __init__(self, persist_dir: str | None = None) -> None:
        self.persist_dir = persist_dir or _default_persist_dir() # type: ignore

    def build_or_load(
        self,
        embedding_model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
    ):
        from langchain_huggingface import HuggingFaceEmbeddings  # type: ignore
        from langchain_community.vectorstores import Chroma  # type: ignore

        embeddings = HuggingFaceEmbeddings(
            model_name=embedding_model_name
        )

        os.makedirs(self.persist_dir, exist_ok=True)

        return Chroma(
            collection_name="synapse_ai_docs",
            embedding_function=embeddings,
            persist_directory=self.persist_dir,
        )

    def add_texts(
        self,
        texts: Iterable[str], # type: ignore
        metadatas: Optional[list[dict]] = None, # type: ignore
        ids: Optional[list[str]] = None, # type: ignore
        embedding_model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
    ) -> int:
        vector_store = self.build_or_load(
            embedding_model_name=embedding_model_name
        )

        texts_list = list(texts)

        if not texts_list:
            return 0

        vector_store.add_texts(
            texts=texts_list,
            metadatas=metadatas,
            ids=ids,
        )

        vector_store.persist()

        return len(texts_list)