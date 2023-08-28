from typing import Literal

from pydantic import BaseModel


class LiveRoom(BaseModel):
    """直播间模型"""

    title: str
    """直播间标题"""
    room_id: int
    """直播间实际房间号"""
    uid: int
    """主播mid"""
    online: int
    """直播间在线人数"""
    live_time: int
    """直播持续时长"""
    live_status: Literal[0, 1, 2]
    """直播间开播状态（0：未开播，1：正在直播，2：轮播中）"""
    short_id: int
    """直播间短房间号，常见于签约主播"""
    area: int
    """直播间分区id"""
    area_name: str
    """直播间分区名"""
    area_v2_id: int
    """直播间新版分区id"""
    area_v2_name: str
    """直播间新版分区名"""
    area_v2_parent_id: int
    """直播间父分区id"""
    area_v2_parent_name: str
    """直播间父分区名"""
    uname: str
    """主播用户名"""
    face: str
    """主播头像url"""
    tag_name: str
    """直播间标签"""
    tags: str
    """直播间自定标签"""
    cover_from_user: str
    """直播间封面url"""
    keyframe: str
    """直播间关键帧url"""
    lock_till: str
    """直播间封禁信息"""
    hidden_till: str
    """直播间隐藏信息"""
    broadcast_type: Literal[0, 1]
    """直播类型（0:普通直播，1：手机直播）"""
