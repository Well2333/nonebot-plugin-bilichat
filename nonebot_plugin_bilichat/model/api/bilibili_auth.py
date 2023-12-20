from pydantic import BaseModel


class AuthInfo(BaseModel):
    id: int
    token_expired: int
    cookie_expired: int

class Qrcode(BaseModel):
    qrcode_url: str
    auth_code: str
