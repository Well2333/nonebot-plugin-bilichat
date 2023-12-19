from typing import Any

from pydantic import BaseModel


class Response(BaseModel):
    code: int = 0
    message: str = ""
    data: Any = {}

class FaildResponse(BaseModel):
    code: int
    message: str