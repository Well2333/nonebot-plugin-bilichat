
from nonebot_plugin_auto_bot_selector.target import SupportedPlatform
from pydantic import BaseModel, Field


class SubsConfig(BaseModel):
    subs_limit: int = Field(5, ge=0, le=50)
    dynamic_interval: int = Field(90, ge=10)
    live_interval: int = Field(30, ge=10)
    push_delay: int = Field(3, ge=0)
    dynamic_grpc: bool = False


class UserSubConfig(BaseModel):
    uid: int
    dynamic: bool = True
    dynamic_at_all: bool = False
    live: bool = True
    live_at_all: bool = False


class User(BaseModel):
    user_id: str
    platform: SupportedPlatform
    at_all: bool = False
    subscriptions: list[UserSubConfig]


class Uploader(BaseModel):
    uid: int
    nickname: str = ""


class Subs(BaseModel):
    config: SubsConfig
    uploaders: list[Uploader] = []
    users: list[User] = []
