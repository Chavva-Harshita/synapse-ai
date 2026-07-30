from pydantic import BaseModel # type: ignore


class RetrieveRequest(BaseModel):
    query: str
    top_k: int = 3


class RetrievedChunk(BaseModel):
    source_text: str
    metadata: dict
    similarity: float | None = None


class RetrieveResponse(BaseModel):
    query: str
    results: list[RetrievedChunk]

