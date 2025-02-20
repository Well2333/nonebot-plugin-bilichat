from asyncio import Lock
from typing import Literal

from nonebot.log import logger
from nonebot_plugin_uninfo.target import to_target
from pydantic import BaseModel

from nonebot_plugin_bilichat.config import ConfigCTX
from nonebot_plugin_bilichat.model.exception import AbortError
from nonebot_plugin_bilichat.model.subscribe import PushType, UserInfo


class UPStatus(BaseModel):
    uid: int
    """up主的mid"""
    name: str
    """up主的名字"""
    dyn_offset: int = -1
    """最新的动态id"""
    live_status: int = -1
    """直播状态, 0: 未开播, 1: 开播, 2: 轮播"""
    live_time: int = 0
    """直播开始时间"""
    
    def set_name(self, name: str) -> None:
        self.name = name
        for user in self.users:
            user.subscribes_dict[self.uid].uname = name
        ConfigCTX.set()

    @property
    def users(self) -> list[UserInfo]:
        return [user for user in SubsStatus.online_users.values() if user.subscribes_dict.get(self.uid)]


class SubsStatus:
    online_users: dict[str, UserInfo] = {}  # noqa: RUF012
    """在线的用户"""
    modify_lock = Lock()
    """用户锁"""
    online_ups_cache: dict[int, UPStatus] = {}  # noqa: RUF012
    """已激活的up主缓存, up.uid: UPStatus"""

    @classmethod
    async def refresh_online_users(cls) -> None:
        logger.debug("重新检查可推送的用户")
        async with cls.modify_lock:
            cls.online_users.clear()
            config = ConfigCTX.get()
            for user in config.subs.users_dict.copy().values():
                # 清理无订阅的用户
                if not user.subscribes_dict:
                    config.subs.users_dict.pop(user.id)
                    ConfigCTX.set()
                    continue
                # 检查用户是否在线
                target = to_target(user.info)
                try:
                    bot = await target.select()
                    logger.debug(f"用户 [{user.id}] 在线, 可用的bot: {bot}")
                    cls.online_users[user.id] = user
                except Exception as e:
                    logger.debug(f"用户 [{user.id}] 未在线: {e}")
            logger.debug(f"当前可推送的用户: {list(cls.online_users.keys()) or '无'}")

    @classmethod
    async def get_online_ups(cls, type_: Literal["dynamic", "live"]) -> list[UPStatus]:
        await cls.refresh_online_users()
        if not cls.online_users:
            raise AbortError("没有可用激活的用户, 跳过")

        online_ups: list[UPStatus] = []
        for user in cls.online_users.values():
            for up in user.subscribes_dict.values():
                if (type_ == "dynamic" and all(b == PushType.IGNORE for b in up.dynamic.values())) or (
                    type_ == "live" and up.live == PushType.IGNORE
                ):
                    continue
                up_status = cls.online_ups_cache.get(up.uid, UPStatus(uid=up.uid, name=up.uname))
                cls.online_ups_cache[up.uid] = up_status
                if up_status not in online_ups:
                    online_ups.append(up_status)

        if not online_ups:
            raise AbortError(f"{type_} 类型没有需要推送的up主, 跳过")

        return online_ups
