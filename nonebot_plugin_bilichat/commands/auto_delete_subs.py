from typing import Union

from nonebot.log import logger
from nonebot.plugin import on_notice

from ..subscribe import LOCK
from ..subscribe.manager import SubscriptionSystem

auto_delete_subs = on_notice(block=False)

try:
    from nonebot.adapters.mirai2.event import BotLeaveEventActive, BotLeaveEventDisband, BotLeaveEventKick

    @auto_delete_subs.handle()
    async def remove_sub_mirai2(event: Union[BotLeaveEventKick, BotLeaveEventDisband, BotLeaveEventActive]):
        logger.info(f"remove subs from {event.group.id}")
        async with LOCK:
            if user := SubscriptionSystem.users.get("mirai2-_-" + str(event.group.id)):
                for up in user.subscribe_ups:
                    await user.remove_subscription(up)
            SubscriptionSystem.save_to_file()

except ImportError:
    pass

try:
    from nonebot.adapters.onebot.v11 import GroupDecreaseNoticeEvent

    @auto_delete_subs.handle()
    async def remove_sub_v11(event: GroupDecreaseNoticeEvent):
        if not event.is_tome():
            return
        logger.info(f"remove subs from {event.group_id}")
        async with LOCK:
            if user := SubscriptionSystem.users.get("OneBot V11-_-" + str(event.group_id)):
                for up in user.subscribe_ups:
                    await user.remove_subscription(up)
            SubscriptionSystem.save_to_file()

except ImportError:
    pass
