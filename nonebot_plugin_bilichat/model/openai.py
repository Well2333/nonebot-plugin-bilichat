from pydantic import BaseModel


class AISummary(BaseModel):
    error: bool = False
    message: str = ""
    summary: str = ""
    raw: dict = {}
