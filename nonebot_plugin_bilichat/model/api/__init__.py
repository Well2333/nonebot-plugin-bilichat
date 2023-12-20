from typing import Generic, Optional, TypeVar

from pydantic import BaseModel
from pydantic.generics import GenericModel

DataType = TypeVar("DataType")


class Response(GenericModel, Generic[DataType]):
    code: int = 0
    message: str = ""
    data: Optional[DataType]


class FaildResponse(BaseModel):
    code: int
    message: str
