from nonebot.adapters.onebot.v11 import (
    GroupDecreaseNoticeEvent,
)
from nonebot.log import logger
from nonebot.plugin import on_notice

from ..subscribe.manager import SubscriptionSystem


async def check_ban(event: GroupDecreaseNoticeEvent):
    if event.is_tome():
        return True
    return False


leave_group = on_notice(rule=check_ban)

@leave_group.handle()
async def remove_sub(event: GroupDecreaseNoticeEvent):
    logger.info(f"remove subs from {event.group_id}")
    if user := SubscriptionSystem.users.get(str(event.group_id)):
        for up in user.subscribe_ups:
            await user.remove_subscription(up)
    SubscriptionSystem.save_to_file()