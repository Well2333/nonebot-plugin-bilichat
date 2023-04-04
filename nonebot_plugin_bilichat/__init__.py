import re

from lib.b23_extract import b23_extract
from nonebot.adapters.onebot.v12.event import (
    GroupMessageEvent,
    MessageEvent,
    PrivateMessageEvent,
)
from nonebot.consts import REGEX_STR
from nonebot.plugin import PluginMetadata, on_keyword, on_regex
from nonebot.rule import Rule
from nonebot.typing import T_State

from .config import plugin_config

__plugin_meta__ = PluginMetadata(
    name="nonebot-plugin-bilichat",
    description="一个通过 OpenAI 来对b站视频进行总结插件",
    usage="直接发送视频链接即可",
    extra={
        "author": "djkcyl",
        "version": "0.1.0",
        "priority": 1,
    },
)


RE_PATTERN = r"av(\d{1,15})|BV(1[A-Za-z0-9]{2}4.1.7[A-Za-z0-9]{2})"


async def _bili_check(event: MessageEvent):
    if isinstance(event, PrivateMessageEvent):
        return True
    elif isinstance(event, GroupMessageEvent):
        return event.group_id in plugin_config.bili_whitelist


bili = on_regex(
    RE_PATTERN,
    block=plugin_config.bili_block,
    priority=1,
    rule=Rule(_bili_check), # type: ignore
)


@bili.handle()
async def get_bili_number_re(state: T_State):
    state["bili_number"] = state[REGEX_STR]


b23 = on_keyword(
    {"b23.tv", "b23.wtf"},
    block=plugin_config.bili_block,
    priority=1,
    rule=Rule(_bili_check), # type: ignore
)


@b23.handle()
async def get_bili_number_b23(state: T_State, event: MessageEvent):
    if matched := re.search(RE_PATTERN, b23_extract(event.get_plaintext())): # type: ignore
        state["bili_number"] = matched.group()


@bili.handle()
@b23.handle()
async def main(state: T_State, event: MessageEvent):
    bili_number = state["bili_number"]
