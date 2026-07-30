from pydantic import BaseModel # type: ignore


class ExtractTextResponse(BaseModel):
    document: dict
    text: str

