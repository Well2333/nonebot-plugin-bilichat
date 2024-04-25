from typing import Generic, TypeVar

from nonebot.compat import PYDANTIC_V2
from pydantic import BaseModel

DataType = TypeVar("DataType")

if PYDANTIC_V2:

    class Response(BaseModel, Generic[DataType]):  # type: ignore
        code: int = 0
        message: str = ""
        data: DataType | None

else:
    from pydantic.generics import GenericModel

    class Response(GenericModel, Generic[DataType]):
        code: int = 0
        message: str = ""
        data: DataType | None


class FaildResponse(BaseModel):
    code: int
    message: str
