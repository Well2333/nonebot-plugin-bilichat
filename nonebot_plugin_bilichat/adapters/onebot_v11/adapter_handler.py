from typing import TYPE_CHECKING, List, Set, Union

from nonebot import get_bots
from nonebot.adapters.onebot.v11 import (
    Bot,
    GroupMessageEvent,
    Message,
    MessageEvent,
    MessageSegment,
)
from nonebot.log import logger

if TYPE_CHECKING:
    from ...subscribe.manager import SubscriptionSystem, Uploader


async def push(user_id: str, content: List[Union[str, bytes]], at_all: bool = False):
    message = Message()
    if at_all:
        message.append(MessageSegment.at("all"))
    for c in content:
        if isinstance(c, str):
            message.append(MessageSegment.text(c))
        elif isinstance(c, bytes):
            message.append(MessageSegment.image(file=c))

    bots = get_bots().values()
    for bot in bots:
        if isinstance(bot, Bot):
            groups = await bot.get_group_list()
            for group in groups:
                if int(user_id) == group["group_id"]:
                    try:
                        await bot.send_group_msg(group_id=int(user_id), message=message)
                        return
                    except Exception as e:
                        logger.exception(e)


async def get_user_id(event: MessageEvent):
    if isinstance(event, GroupMessageEvent):
        return event.group_id
    return None


async def get_activate_ups(subsys: "SubscriptionSystem") -> Set["Uploader"]:
    ups = set()
    for bot in get_bots().values():
        if not isinstance(bot, Bot):
            continue
        groups = await bot.get_group_list()
        for group in groups:
            if user := subsys.users.get("OneBot V11-_-" + str(group["group_id"])):
                ups.update(user.subscribe_ups)
    return ups
