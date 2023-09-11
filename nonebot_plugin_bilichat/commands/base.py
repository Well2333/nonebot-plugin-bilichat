from nonebot.adapters import Bot, Event
from nonebot.exception import FinishedException
from nonebot.matcher import Matcher
from nonebot.plugin import CommandGroup
from nonebot.rule import to_me

from ..config import plugin_config
from ..subscribe import LOCK
from ..subscribe.manager import SubscriptionSystem, User
from .adapters import ID_HANDLER

bilichat = CommandGroup(
    plugin_config.bilichat_cmd_start,
    rule=to_me() if plugin_config.bilichat_command_to_me else None,
)


async def get_user(matcher: Matcher, bot: Bot, event: Event) -> User:
    if LOCK.locked():
        await matcher.finish("正在刷取动态/直播呢，稍等几秒再试吧\n`(*>﹏<*)′")
    handler = ID_HANDLER.get(bot.adapter.get_name())
    # 获取用户对象
    if not handler:
        await matcher.finish("暂时还不支持当前平台呢\n`(*>﹏<*)′")
        raise FinishedException
    user_id = str(await handler(event))
    if not user_id:
        await matcher.finish("暂时还不支持当前会话呢\n`(*>﹏<*)′")
        raise FinishedException
    return SubscriptionSystem.users.get(
        f"{bot.adapter.get_name()}-_-{user_id}", User(user_id=user_id, platfrom=bot.adapter.get_name())
    )
