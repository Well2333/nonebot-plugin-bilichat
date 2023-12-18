from asyncio import Lock

from nonebot.matcher import Matcher
from nonebot.params import Depends
from nonebot.plugin import CommandGroup
from nonebot.rule import to_me
from nonebot_plugin_saa import SaaTarget

from ..config import plugin_config
from ..subscribe import LOCK
from ..subscribe.manager import SubscriptionSystem, User

bilichat = CommandGroup(
    plugin_config.bilichat_cmd_start,
    rule=to_me() if plugin_config.bilichat_command_to_me else None,
)


async def check_lock(matcher: Matcher) -> Lock:
    if LOCK.locked():
        await matcher.finish("正在刷取动态/直播呢，稍等几秒再试吧\n`(*>﹏<*)′")
    return LOCK


async def get_user(matcher: Matcher, target: SaaTarget, lock: Lock = Depends(check_lock)):
    async with lock:
        platform, user_id = User.extract_saa_target(target)
        if not user_id:
            await matcher.finish("暂时还不支持当前会话呢\n`(*>﹏<*)′")
        return SubscriptionSystem.users.get(f"{platform}-_-{user_id}", User(user_id=user_id, platform=platform))
