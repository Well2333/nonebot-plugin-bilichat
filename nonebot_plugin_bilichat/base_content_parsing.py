import asyncio
import base64
import shlex

from nonebot.adapters import Bot, Event
from nonebot.exception import FinishedException
from nonebot.log import logger
from nonebot.plugin import on_message
from nonebot.rule import Rule
from nonebot.typing import T_State
from nonebot_plugin_alconna.uniseg import Hyper, Image, MsgTarget, Reply, Text, UniMessage, UniMsg

from .config import config
from .lib.content_cd import BilichatCD
from .model.arguments import Options, parser
from .model.exception import AbortError, RequestError
from .model.request_api import Content
from .request_api import get_request_api

lock = asyncio.Lock()


async def _permission_check(bot: Bot, event: Event, target: MsgTarget, state: T_State) -> bool:
    state["_uid_"] = target.id
    # 自身消息
    _id = target.id if target.private else event.get_user_id()
    if _id == bot.self_id:
        if config.nonebot.only_self or config.nonebot.enable_self:
            return True
        elif not config.nonebot.enable_self:
            return False
    # 不是自身消息但开启了仅自身
    elif config.nonebot.only_self:
        return False
    # 是否 to me
    if config.nonebot.only_to_me and not event.is_tome():  # noqa: SIM103
        return False
    # return plugin_config.verify_permission(target.id)
    return True


async def _bili_check(state: T_State, event: Event, bot: Bot, msg: UniMsg) -> bool:
    api = get_request_api()
    _msgs = msg.copy()
    if Reply in msg and (
        (config.nonebot.enable_self and str(event.get_user_id()) == str(bot.self_id)) or event.is_tome()
    ):
        # 如果是回复消息
        # 1. 如果是自身消息且允许自身消息
        # 2. 如果被回复消息中包含对自身的at
        # 满足上述任一条件, 则将被回复的消息的内容添加到待解析的内容中
        _msgs.append(Text(str(msg[Reply, 0].msg)))

    bililink = None
    for _msg in _msgs[Text] + _msgs[Hyper]:
        # b23 格式的链接
        _msg_str = str(_msg.data)
        if "b23" in _msg_str:
            bililink = await api.tools_b23_extract(_msg_str)
        # av bv cv 格式和动态的链接
        for seg in ("av", "bv", "cv", "dynamic", "opus", "t.bilibili.com"):
            if seg in _msg_str.lower():
                bililink = _msg_str
                break

    if not bililink:
        return False

    options: Options = state["_options_"]

    try:
        content = await api.content_all(bililink)
        if options.force:
            BilichatCD.record_cd(state["_uid_"], str(content.id))
        else:
            BilichatCD.check_cd(state["_uid_"], str(content.id))
        state["_raw_cont_"] = content
        return True  # noqa: TRY300
    except AbortError as e:
        logger.info(e)
        return False
    except FinishedException:
        return False


def set_options(state: T_State, msg: UniMsg):
    options = parser.parse_known_args(args=shlex.split(msg.extract_plain_text()), namespace=Options())[0]
    state["_options_"] = options
    if options:
        logger.info(f"已设置参数: {options}")


async def _pre_check(state: T_State, event: Event, bot: Bot, msg: UniMsg, target: MsgTarget) -> bool:
    set_options(state, msg)
    return await _permission_check(bot, event, target, state) and await _bili_check(state, event, bot, msg)


bilichat = on_message(
    block=config.nonebot.block,
    priority=2,
    rule=Rule(_pre_check),
)


@bilichat.handle()
async def content_info(origin_msg: UniMsg, state: T_State):
    msgs = UniMessage()
    reply = Reply(id=origin_msg.get_message_id())
    msgs.append(reply)
    try:
        raw_cont: Content = state["_raw_cont_"]
        if raw_cont.type == "video":
            content = await get_request_api().content_video(raw_cont.id, config.api.browser_shot_quality)
        elif raw_cont.type == "column":
            content = await get_request_api().content_column(raw_cont.id, config.api.browser_shot_quality)
        elif raw_cont.type == "dynamic":
            content = await get_request_api().content_dynamic(raw_cont.id, config.api.browser_shot_quality)
        else:
            raise ValueError(f"未知的内容类型: {raw_cont.type}")
        msgs.append(Image(raw=base64.b64decode(content.img)))
        msgs.append(Text(content.b23))
    except RequestError as e:
        logger.error(e)
        msgs.append(Text(f"{e.type}: {e.message}"))

    receipt = await msgs.send()
