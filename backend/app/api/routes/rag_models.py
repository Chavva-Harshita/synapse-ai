from uuid import UUID

from pydantic import BaseModel, Field, field_validator # type: ignore


class RAGChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=4000)
    document_id: UUID
    top_k: int = Field(default=5, ge=1, le=20)

    @field_validator("message")
    @classmethod
    def message_must_not_be_blank(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("Question must not be empty")
        return normalized


class RAGChatResponse(BaseModel):
    reply: str
    retrieved_chunks: list[dict]
    document_id: str
