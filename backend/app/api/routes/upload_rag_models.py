from pydantic import BaseModel # type: ignore


class UploadRagResponse(BaseModel):
    # Stored PDF document info
    document: dict

    # Chunking + embedding stats
    stored: int
    chunk_count: int
    chunk_size: int
    chunk_overlap: int

