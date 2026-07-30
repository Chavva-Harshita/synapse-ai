from pydantic import BaseModel


class ChunkedDocument(BaseModel):
    chunks: list[str]
    chunk_size: int
    chunk_overlap: int


