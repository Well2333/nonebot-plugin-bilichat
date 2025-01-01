from asyncio import Lock

from nonebot.log import logger
from nonebot_plugin_uninfo.target import to_target
from pydantic import BaseModel

from nonebot_plugin_bilichat.config import config
from nonebot_plugin_bilichat.model.exception import AbortError
from nonebot_plugin_bilichat.model.subscribe import User


class UPStatus(BaseModel):
    uid: int
    """up主的mid"""
    name: str
    """up主的名字"""
    dyn_offset: int = -1
    """最新的动态id"""
    live_status: int = -1
    """直播状态, 0: 未开播, 1: 开播, 2: 轮播"""

    @property
    def users(self) -> list[User]:
        return [user for user in SubsStatus.online_users.values() if user.subscribes.get(str(self.uid))]


class SubsStatus:
    online_users: dict[str, User] = {}  # noqa: RUF012
    """在线的用户"""
    modify_lock = Lock()
    """用户锁"""
    online_ups_cache: dict[int, UPStatus] = {}
    """已激活的up主缓存, up.uid: UPStatus"""

    @classmethod
    async def refresh_online_users(cls) -> None:
        logger.info("重新检查可推送的用户")
        async with cls.modify_lock:
            cls.online_users.clear()
            for user in config.subs.users.values():
                target = to_target(user.info)
                try:
                    bot = await target.select()
                    logger.info(f"用户 [{user.info.id}] 在线, 可用的bot: {bot}")
                    cls.online_users[user.info.id] = user
                except Exception as e:
                    logger.warning(f"用户 [{user.info.id}] 未在线: {e}")
            logger.info(f"当前可推送的用户: {cls.online_users}")

    @classmethod
    async def get_online_ups(cls) -> list[UPStatus]:
        if not cls.online_users:
            await cls.refresh_online_users()
            if not cls.online_users:
                raise AbortError("没有可用激活的用户, 跳过")

        online_ups = []
        for user in cls.online_users.values():
            for up in user.subscribes.values():
                up_status = cls.online_ups_cache.get(up.uid, UPStatus(uid=up.uid, name=up.uname))
                online_ups.append(up_status)
                cls.online_ups_cache[up.uid] = up_status

        return online_ups
