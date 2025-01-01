import base64
from datetime import datetime
from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel


class VersionInfo(BaseModel):
    response_datetime: datetime
    """请求时间"""
    package: str
    """包名"""
    version: str
    """版本号"""
    bilichat_min_version: str
    """Bilichat 最低版本号"""


class Note(BaseModel):
    create_time: str
    """Create Time"""
    source: str
    """Source"""


class Account(BaseModel):
    cookies: dict[str, Any]
    note: Note
    uid: int

    def __str__(self) -> str:
        return f"{self.uid}({self.note.source})"


class DynamicType(str, Enum):
    DYNAMIC_TYPE_AD = "DYNAMIC_TYPE_AD"
    DYNAMIC_TYPE_APPLET = "DYNAMIC_TYPE_APPLET"
    DYNAMIC_TYPE_ARTICLE = "DYNAMIC_TYPE_ARTICLE"
    DYNAMIC_TYPE_AV = "DYNAMIC_TYPE_AV"
    DYNAMIC_TYPE_BANNER = "DYNAMIC_TYPE_BANNER"
    DYNAMIC_TYPE_COMMON_SQUARE = "DYNAMIC_TYPE_COMMON_SQUARE"
    DYNAMIC_TYPE_COMMON_VERTICAL = "DYNAMIC_TYPE_COMMON_VERTICAL"
    DYNAMIC_TYPE_COURSES = "DYNAMIC_TYPE_COURSES"
    DYNAMIC_TYPE_COURSES_BATCH = "DYNAMIC_TYPE_COURSES_BATCH"
    DYNAMIC_TYPE_COURSES_SEASON = "DYNAMIC_TYPE_COURSES_SEASON"
    DYNAMIC_TYPE_DRAW = "DYNAMIC_TYPE_DRAW"
    DYNAMIC_TYPE_FORWARD = "DYNAMIC_TYPE_FORWARD"
    DYNAMIC_TYPE_LIVE = "DYNAMIC_TYPE_LIVE"
    DYNAMIC_TYPE_LIVE_RCMD = "DYNAMIC_TYPE_LIVE_RCMD"
    DYNAMIC_TYPE_MEDIALIST = "DYNAMIC_TYPE_MEDIALIST"
    DYNAMIC_TYPE_MUSIC = "DYNAMIC_TYPE_MUSIC"
    DYNAMIC_TYPE_NONE = "DYNAMIC_TYPE_NONE"
    DYNAMIC_TYPE_PGC = "DYNAMIC_TYPE_PGC"
    DYNAMIC_TYPE_SUBSCRIPTION = "DYNAMIC_TYPE_SUBSCRIPTION"
    DYNAMIC_TYPE_SUBSCRIPTION_NEW = "DYNAMIC_TYPE_SUBSCRIPTION_NEW"
    DYNAMIC_TYPE_UGC_SEASON = "DYNAMIC_TYPE_UGC_SEASON"
    DYNAMIC_TYPE_WORD = "DYNAMIC_TYPE_WORD"


class Dynamic(BaseModel):
    dyn_id: int
    dyn_timestamp: int
    dyn_type: DynamicType


class LiveRoom(BaseModel):
    area: int
    area_name: str
    area_v2_id: int
    area_v2_name: str
    area_v2_parent_id: int
    area_v2_parent_name: str
    broadcast_type: int
    cover_from_user: str
    face: str
    hidden_till: str
    keyframe: str
    live_status: int
    live_time: int
    lock_till: str
    online: int
    room_id: int
    short_id: int
    tag_name: str
    tags: str
    title: str
    uid: int
    uname: str


class Content(BaseModel):
    type: Literal["video", "column", "dynamic"]
    id: str
    b23: str
    img: str

    @property
    def img_bytes(self) -> bytes:
        return base64.b64decode(self.img)


class SearchUp(BaseModel):
    nickname: str
    uid: int

    def __str__(self) -> str:
        return f"{self.nickname}({self.uid})"
