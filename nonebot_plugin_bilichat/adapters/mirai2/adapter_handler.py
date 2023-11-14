import base64
from typing import TYPE_CHECKING, List, Set, Union

from nonebot import get_bots
from nonebot.adapters.mirai2 import Bot
from nonebot.adapters.mirai2.event import (
    GroupMessage,
    MessageEvent,
)
from nonebot.adapters.mirai2.message import MessageChain, MessageSegment
from nonebot.log import logger

if TYPE_CHECKING:
    from ...subscribe.manager import SubscriptionSystem, Uploader


async def push(user_id: str, content: List[Union[str, bytes]], at_all: bool = False):
    message = MessageChain("")
    if at_all:
        message.append(MessageSegment.at_all())
    for c in content:
        if isinstance(c, str):
            message.append(c)
        elif isinstance(c, bytes):
            message.append(MessageSegment.image(base64=base64.b64encode(c).decode("utf-8")))

    bots = get_bots().values()
    for bot in bots:
        if isinstance(bot, Bot):
            groups = (await bot.group_list())["data"]
            for group in groups:
                if int(user_id) == group["id"]:
                    try:
                        await bot.send_group_message(target=int(user_id), message_chain=message, quote=None)
                        return
                    except Exception as e:
                        logger.exception(e)


async def get_user_id(event: MessageEvent):
    if isinstance(event, GroupMessage):
        return event.sender.group.id
    return None


async def get_activate_ups(subsys: "SubscriptionSystem") -> Set["Uploader"]:
    ups = set()
    for bot in get_bots().values():
        if not isinstance(bot, Bot):
            continue
        groups = (await bot.group_list())["data"]
        for group in groups:
            if user := subsys.users.get("mirai2-_-" + str(group["id"])):
                ups.update(user.subscribe_ups)
    return ups