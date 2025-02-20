import asyncio
from asyncio import Lock

from nonebot.log import logger
from nonebot.plugin import CommandGroup
from nonebot.rule import to_me
from nonebot_plugin_uninfo import Uninfo

from nonebot_plugin_bilichat.config import ConfigCTX
from nonebot_plugin_bilichat.model.subscribe import UserInfo
from nonebot_plugin_bilichat.subscribe.status import SubsStatus

bilichat = CommandGroup(
    ConfigCTX.get().nonebot.cmd_start,
    rule=to_me() if ConfigCTX.get().nonebot.command_to_me else None,
    block=ConfigCTX.get().nonebot.block,
)


async def check_lock() -> Lock:
    while SubsStatus.modify_lock.locked():
        await asyncio.sleep(0)
    return SubsStatus.modify_lock


async def get_user(session: Uninfo) -> UserInfo:
    user = ConfigCTX.get().subs.users_dict.get(
        f"{session.scope}_type{session.scene.type}_{session.scene.id}",
        UserInfo(info=session, subscribes={}),
    )
    logger.info(f"get user: {user.id}")
    return user
