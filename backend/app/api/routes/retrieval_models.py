from pydantic import BaseModel, Field, field_validator # type: ignore


class RetrieveRequest(BaseModel):
    query: str = Field(min_length=1, max_length=4000)
    top_k: int = Field(default=3, ge=1, le=20)

    @field_validator("query")
    @classmethod
    def query_must_not_be_blank(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("Query must not be empty")
        return normalized


class RetrievedChunk(BaseModel):
    source_text: str
    metadata: dict
    similarity: float | None = None


class RetrieveResponse(BaseModel):
    query: str
    results: list[RetrievedChunk]
