from enum import Enum
from typing import overload

from nonebot_plugin_alconna import Target
from nonebot_plugin_uninfo import Session
from nonebot_plugin_uninfo.target import to_target
from pydantic import BaseModel, field_validator

from nonebot_plugin_bilichat.model.request_api import DynamicType


class PushType(str, Enum):
    """推送方式"""

    AT_ALL = "AT_ALL"
    PUSH = "PUSH"
    IGNORE = "IGNORE"


DYNAMIC_IGNORE_TYPE = {
    DynamicType.DYNAMIC_TYPE_AD,
    DynamicType.DYNAMIC_TYPE_LIVE,
    DynamicType.DYNAMIC_TYPE_LIVE_RCMD,
    DynamicType.DYNAMIC_TYPE_BANNER,
}
DEFUALT_DYNAMIC_PUSH_TYPE: dict[DynamicType, PushType] = {
    t: (PushType.IGNORE if t in DYNAMIC_IGNORE_TYPE else PushType.PUSH) for t in DynamicType
}


class UP(BaseModel):
    uid: int
    """UP主UID"""
    uname: str = ""
    """UP主B站用户名"""
    nickname: str = ""
    """UP主昵称, 可自行设置"""
    note: str = ""
    """备注"""
    dynamic: dict[DynamicType, PushType] = DEFUALT_DYNAMIC_PUSH_TYPE.copy()
    """各种类型动态推送方式"""
    live: PushType = PushType.PUSH
    """直播推送方式"""


class User(BaseModel):
    info: Session
    subscribes: dict[str, UP] = {}
    """订阅的UP主, UP.uid: UP"""

    @field_validator("info", mode="before")
    @classmethod
    def construct_info(cls, value: dict | Session) -> Session:
        if isinstance(value, dict):
            value["member"] = None
            return Session.load(value)
        value.member = None
        return value

    @property
    def target(self) -> Target:
        return to_target(self.info)

    @property
    def id(self) -> str:
        return f"{self.info.scope}_type{self.info.scene.type}_{self.info.scene.id}"

    @overload
    def add_subscription(self, *, uid: int | str, uname: str) -> None: ...

    @overload
    def add_subscription(self, *, up: UP) -> None: ...

    def add_subscription(self, *, uid: int | str | None = None, uname: str | None = None, up: UP | None = None):
        if up:
            self.subscribes[str(up.uid)] = up
        elif uid and uname:
            self.subscribes[str(uid)] = UP(uid=int(uid), uname=uname)
        else:
            raise ValueError("uid uname 和 up 不能同时为空")
