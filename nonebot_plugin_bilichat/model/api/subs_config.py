from typing import List

from nonebot_plugin_saa.utils.const import SupportedPlatform
from pydantic import BaseModel, Extra, Field


class SubsConfig(BaseModel):
    subs_limit: int = Field(5, ge=0, le=50)
    dynamic_interval: int = Field(90, ge=60)
    live_interval: int = Field(30, ge=10)
    push_delay: int = Field(3, ge=0)
    dynamic_grpc: bool = False

    class Config:
        extra = Extra.ignore


class UserSubConfig(BaseModel):
    uid: int
    dynamic: bool = True
    dynamic_at_all: bool = False
    live: bool = True
    live_at_all: bool = False

    class Config:
        extra = Extra.ignore


class User(BaseModel):
    user_id: str
    platform: SupportedPlatform
    at_all: bool = False
    subscriptions: List[UserSubConfig]

    class Config:
        extra = Extra.ignore


class Uploader(BaseModel):
    uid: int
    nickname: str = ""

    class Config:
        extra = Extra.ignore


class Subs(BaseModel):
    config: SubsConfig
    uploaders: List[Uploader] = []
    users: List[User] = []

    class Config:
        extra = Extra.ignore
