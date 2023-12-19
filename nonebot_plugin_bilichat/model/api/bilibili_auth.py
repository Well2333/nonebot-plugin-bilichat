from typing import List

from pydantic import BaseModel

from . import Response


class AuthInfo(BaseModel):
    id: int
    token_expired: int
    cookie_expired: int


class ListAuthResponse(Response):
    data: List[AuthInfo]


class SingleAuthResponse(Response):
    data: AuthInfo


class Qrcode(BaseModel):
    qrcode_url: str
    auth_code: str

class GenQrcodeResponse(Response):
    data: Qrcode
