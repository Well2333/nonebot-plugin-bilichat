from typing import Union

from nonebot.log import logger
from nonebot.plugin import on_notice
from nonebot_plugin_saa import SaaTarget

from ..subscribe.manager import CONFIG_LOCK, SubscriptionSystem, User

auto_delete_subs = on_notice(block=False)


async def remove_sub(target: SaaTarget):
    platform, user_id = User.extract_saa_target(target)
    logger.info(f"remove subs from {user_id}")
    async with CONFIG_LOCK:
        if user := SubscriptionSystem.users.get(f"{platform}-_-{user_id}"):
            for up in user.subscribe_ups:
                await user.remove_subscription(up)
        SubscriptionSystem.save_to_file()


try:
    from nonebot.adapters.mirai2.event import BotLeaveEventActive, BotLeaveEventDisband, BotLeaveEventKick

    @auto_delete_subs.handle()
    async def remove_sub_mirai2(
        event: Union[BotLeaveEventKick, BotLeaveEventDisband, BotLeaveEventActive], target: SaaTarget
    ):
        await remove_sub(target)

except ImportError:
    pass

try:
    from nonebot.adapters.onebot.v11 import GroupDecreaseNoticeEvent

    @auto_delete_subs.handle()
    async def remove_sub_v11(event: GroupDecreaseNoticeEvent, target: SaaTarget):
        if not event.is_tome():
            return
        await remove_sub(target)

except ImportError:
    pass
