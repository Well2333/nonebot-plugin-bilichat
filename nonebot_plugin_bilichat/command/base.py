import asyncio
from asyncio import Lock

from nonebot.plugin import CommandGroup
from nonebot.rule import to_me
from nonebot_plugin_uninfo import Uninfo

from nonebot_plugin_bilichat.config import config
from nonebot_plugin_bilichat.model.subscribe import User
from nonebot_plugin_bilichat.subscribe.status import SubsStatus

bilichat = CommandGroup(
    config.nonebot.cmd_start,
    rule=to_me() if config.nonebot.command_to_me else None,
)


async def check_lock() -> Lock:
    while SubsStatus.modify_lock.locked():
        await asyncio.sleep(0)
    return SubsStatus.modify_lock


async def get_user(session: Uninfo) -> User:
    return config.subs.users.get(session.id, User(info=session, subscribes={}))