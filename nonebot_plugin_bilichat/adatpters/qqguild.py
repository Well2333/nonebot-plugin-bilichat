import re
import shlex
from itertools import chain
from typing import Union, cast

from nonebot.adapters.qqguild import (
    Bot,
    Message,
    MessageEvent,
    MessageSegment,
)
from nonebot.params import Depends
from nonebot.plugin import on_message
from nonebot.rule import Rule
from nonebot.typing import T_State

from ..config import plugin_config
from ..content import Column, Video
from ..lib.b23_extract import b23_extract
from ..model.arguments import Options, parser
from ..model.exception import AbortError
from . import get_content_info_from_state, get_futuer_fuctions


async def _bili_check(event: MessageEvent, state: T_State):
    _msgs = event.get_message()

    for _msg in _msgs:
        # 如果是图片格式则忽略
        if _msg.type in ("image",):
            continue
        # b23 格式的链接
        _msg_str = str(_msg)
        if "b23" in _msg_str:
            if b23 := re.search(r"b23.(tv|wtf)[\\/]+(\w+)", _msg_str):  # type: ignore
                state["_bililink_"] = await b23_extract(list(b23.groups()))
                return True
        # av bv cv 格式的链接
        for seg in ("av", "bv", "cv"):
            if seg in _msg_str.lower():
                state["_bililink_"] = _msg_str
                return True
    return False


async def _permission_check(bot: Bot, event: MessageEvent, state: T_State):
    # 自身消息
    if str(event.get_user_id()) == str(bot.self_id):
        if plugin_config.bilichat_only_self:
            state["_uid_"] = event.channel_id
            return True
        elif not plugin_config.bilichat_enable_self:
            return False
    elif plugin_config.bilichat_only_self:
        return False
    # 其他消息
    if isinstance(event, MessageEvent):
        state["_uid_"] = f"{event.guild_id}_{event.channel_id}"
        return plugin_config.verify_permission(event.guild_id or "") and plugin_config.verify_permission(
            event.channel_id or ""
        )
    return False


bilichat = on_message(
    block=plugin_config.bilichat_block,
    priority=1,
    rule=Rule(_permission_check, _bili_check),
)


@bilichat.handle()
def set_options(state: T_State, event: MessageEvent):
    state["_options_"] = parser.parse_known_args(
        list(
            chain.from_iterable(
                shlex.split(str(seg)) if cast(MessageSegment, seg).is_text() else (seg,) for seg in event.get_message()
            )
        ),  # type: ignore
        namespace=Options(),
    )[0]


@bilichat.handle()
async def video_info(
    event: MessageEvent,
    content: Union[Column, Video] = Depends(get_content_info_from_state),
):
    if plugin_config.bilichat_basic_info:
        if content_image := await content.get_image(plugin_config.bilichat_basic_info_style):
            await bilichat.send(MessageSegment.file_image(content_image))

    try:
        msgs = []
        for msg in await get_futuer_fuctions(content):
            if msg:
                if isinstance(msg, str):
                    msgs.append(msg)
                elif isinstance(msg, bytes):
                    msgs.append(MessageSegment.file_image(msg))
        if msgs:
            await bilichat.finish(Message(msgs))
    except AbortError as e:
        if plugin_config.bilichat_show_error_msg:
            await bilichat.finish(str(e))
