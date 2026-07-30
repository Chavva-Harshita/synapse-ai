from pydantic import BaseModel # type: ignore
from typing import Optional, List


class RAGChatRequest(BaseModel):
    message: str
    document_id: str
    top_k: int = 5


class RAGChatResponse(BaseModel):
    reply: str
    retrieved_chunks: list[dict]
    document_id: str

