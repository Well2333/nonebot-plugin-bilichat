from enum import Enum

from nonebot_plugin_uninfo import Session
from pydantic import BaseModel

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
    subscribes: dict[str, UP]
