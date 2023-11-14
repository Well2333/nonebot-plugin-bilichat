from typing import TYPE_CHECKING, List, Set, Union

from nonebot import get_bots
from nonebot.adapters.qq import (
    Bot,
    GroupAtMessageCreateEvent,
    GuildMessageEvent,
    MessageEvent,
    MessageSegment,
)
from nonebot.log import logger

from ...lib.tools import obfuscate_urls_in_text

if TYPE_CHECKING:
    from ...subscribe.manager import SubscriptionSystem, Uploader


async def push(user_id: str, content: List[Union[str, bytes]], at_all: bool = False):
    bots = get_bots().values()
    for bot in bots:
        if isinstance(bot, Bot):
            # for guild in await bot.guilds(limit=100):
            #    for channel in await bot.get_channels(guild_id=guild.id):
            #        if user_id == channel.id:
            if user_id.startswith("channel"):
                user_id = user_id[7:]
                try:
                    _at_all_prefix = "@everyone" if at_all else ""
                    for c in content:
                        if isinstance(c, str):
                            c = obfuscate_urls_in_text(c)
                            await bot.send_to_channel(channel_id=user_id, message=_at_all_prefix + c)
                            _at_all_prefix = ""
                        elif isinstance(c, bytes):
                            await bot.send_to_channel(channel_id=user_id, message=MessageSegment.file_image(c))
                    return
                except Exception as e:
                    logger.exception(e)


async def get_user_id(event: MessageEvent):
    if isinstance(event, GuildMessageEvent):
        return "channel" + event.channel_id
    elif isinstance(event, GroupAtMessageCreateEvent):
        return "group" + event.group_id
    return None


async def get_activate_ups(subsys: "SubscriptionSystem") -> Set["Uploader"]:
    ups = set()
    for bot in get_bots().values():
        if not isinstance(bot, Bot):
            continue
        # 频道接口
        for guild in await bot.guilds():
            for channel in await bot.get_channels(guild_id=guild.id):
                if user := subsys.users.get("QQ-_-channel" + channel.id):
                    ups.update(user.subscribe_ups)
    return ups
