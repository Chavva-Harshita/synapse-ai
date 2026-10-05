


from pydantic import BaseModel # type: ignore


class ChunkedDocument(BaseModel):
    chunks: list[str]
    chunk_size: int
    chunk_overlap: int


