from pydantic import BaseModel


class EmbedAndStoreResponse(BaseModel):
    stored: int
    chunk_size: int
    chunk_overlap: int

