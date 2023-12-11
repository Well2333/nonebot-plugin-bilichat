from nonebot.matcher import Matcher
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


async def get_user(matcher: Matcher, target: SaaTarget):
    if LOCK.locked():
        await matcher.finish("正在刷取动态/直播呢，稍等几秒再试吧\n`(*>﹏<*)′")
    async with LOCK:
        platform, user_id = User.extract_saa_target(target)
        if not user_id:
            await matcher.finish("暂时还不支持当前会话呢\n`(*>﹏<*)′")
        return SubscriptionSystem.users.get(f"{platform}-_-{user_id}", User(user_id=user_id, platfrom=platform))
