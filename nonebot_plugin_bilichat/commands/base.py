import asyncio
from asyncio import Lock

from nonebot.log import logger
from nonebot.matcher import Matcher
from nonebot.params import Depends
from nonebot.plugin import CommandGroup
from nonebot.rule import to_me
from nonebot_plugin_alconna.uniseg import MsgTarget

from ..config import plugin_config
from ..subscribe.manager import CONFIG_LOCK, SubscriptionSystem, User

bilichat = CommandGroup(
    plugin_config.bilichat_cmd_start,
    rule=to_me() if plugin_config.bilichat_command_to_me else None,
)


async def check_lock(matcher: Matcher) -> Lock:
    while CONFIG_LOCK.locked():
        await asyncio.sleep(0)
    return CONFIG_LOCK


async def get_user(matcher: Matcher, target: MsgTarget, lock: Lock = Depends(check_lock)):
    logger.debug(target)
    async with lock:
        platform, user_id = User.extract_alc_target(target)
        if not user_id:
            await matcher.finish("暂时还不支持当前会话呢\n`(*>﹏<*)′")
        return SubscriptionSystem.users.get(f"{platform}-_-{user_id}", User(user_id=user_id, platform=platform))
