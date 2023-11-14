import base64
import re
import shlex
from itertools import chain
from typing import Any, Optional, Union, cast

from nonebot.adapters.mirai2 import Bot, MessageChain, MessageSegment
from nonebot.adapters.mirai2.event import FriendMessage, FriendSyncMessage, GroupMessage, GroupSyncMessage, MessageEvent
from nonebot.exception import FinishedException
from nonebot.log import logger
from nonebot.plugin import on_message
from nonebot.rule import Rule
from nonebot.typing import T_State

from ...config import plugin_config
from ...content import Column, Dynamic, Video
from ...lib.b23_extract import b23_extract
from ...model.arguments import Options, parser
from ...model.exception import AbortError
from ...optional import capture_exception
from ..base_content_parsing import get_content_info_from_state, get_futuer_fuctions


async def _bili_check(bot: Bot, event: MessageEvent, state: T_State):
    # 检查并提取 raw_bililink
    if plugin_config.bilichat_enable_self and str(event.get_user_id()) == str(bot.self_id) and event.quote:
        # 是自身消息的情况下，检查是否是回复，是的话则取被回复的消息
        _msgs = event.quote.origin
    else:
        # 其余情况取该条消息
        _msgs = event.get_message()

    for _msg in _msgs:
        # 如果是图片格式则忽略
        if _msg.type in ("Image", "FlashImage", "Voice"):
            continue
        # b23 格式的链接
        _msg_str = str(_msg)
        if "b23" in _msg_str:
            if b23 := re.search(r"b23.(tv|wtf)[\\/]+(\w+)", _msg_str):  # type: ignore
                state["_bililink_"] = await b23_extract(list(b23.groups()))
                return True
        # av bv cv 格式和动态的链接
        for seg in ("av", "bv", "cv", "dynamic", "opus", "t.bilibili.com"):
            if seg in _msg_str.lower():
                state["_bililink_"] = _msg_str
                return True
    return False


async def _permission_check(bot: Bot, event: MessageEvent, state: T_State):
    # 自身消息
    if str(event.get_user_id()) == str(bot.self_id):
        if plugin_config.bilichat_only_self or plugin_config.bilichat_enable_self:
            state["_uid_"] = event.sender.group.id if isinstance(event, GroupMessage) else event.sender.id
            return True
        elif not plugin_config.bilichat_enable_self:
            return False
    elif plugin_config.bilichat_only_self:
        return False
    # 是否 to me
    if plugin_config.bilichat_only_to_me and not event.is_tome():
        return False
    # 私聊消息
    if isinstance(event, FriendMessage):
        state["_uid_"] = event.get_user_id()
        return plugin_config.verify_permission(event.get_user_id())
    # 群聊消息
    elif isinstance(event, GroupMessage):
        state["_uid_"] = event.sender.group.id
        return plugin_config.verify_permission(event.sender.group.id)
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


async def send_msg(
    bot: Bot,
    event: MessageEvent,
    message: Union[str, MessageChain, MessageSegment],
    quote: Optional[int] = None,
) -> Any:
    if not isinstance(message, MessageChain):
        message = MessageChain(message)
    if isinstance(event, (FriendMessage, FriendSyncMessage)):
        return await bot.send_friend_message(target=event.sender.id, message_chain=message, quote=quote)
    elif isinstance(event, GroupMessage):
        return await bot.send_group_message(target=event.sender.group.id, message_chain=message, quote=quote)
    elif isinstance(event, GroupSyncMessage):
        return await bot.send_group_message(target=event.sender.id, message_chain=message, quote=quote)


@bilichat.handle()
async def content_info(bot: Bot, event: MessageEvent, state: T_State):
    messag_id = event.source.id if event.source else None
    try:
        content: Union[Column, Video, Dynamic] = await get_content_info_from_state(state)
    except AbortError as e:
        logger.info(e)
        raise FinishedException
    if plugin_config.bilichat_basic_info:
        content_image = await content.get_image(plugin_config.bilichat_basic_info_style)
        if content_image:
            msgs = MessageChain(MessageSegment.image(base64=base64.b64encode(content_image).decode("utf-8")))
            msgs.append(content.url if plugin_config.bilichat_basic_info_url else content.bili_id)
        else:
            msgs = MessageChain(content.url)
        id_ = await send_msg(bot, event, msgs, quote=messag_id)
        messag_id = id_["messageId"] if plugin_config.bilichat_reply_to_basic_info else messag_id

    try:
        msgs = []
        for msg in await get_futuer_fuctions(content):
            if msg:
                if isinstance(msg, str):
                    msgs.append(msg)
                elif isinstance(msg, bytes):
                    msgs.append(MessageSegment.image(base64=base64.b64encode(msg).decode("utf-8")))
        if msgs:
            await send_msg(bot, event, MessageChain(msgs), quote=messag_id)
    except FinishedException:
        raise
    except AbortError as e:
        if plugin_config.bilichat_show_error_msg:
            await send_msg(bot, event, str(e), quote=messag_id)
    except Exception as e:
        capture_exception()
        logger.exception(e)
        if plugin_config.bilichat_show_error_msg:
            await send_msg(bot, event, str(e), quote=messag_id)
