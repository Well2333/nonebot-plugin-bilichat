import asyncio
import re
import shlex

from nonebot.adapters import Bot, Event
from nonebot.exception import FinishedException
from nonebot.log import logger
from nonebot.plugin import on_message
from nonebot.rule import Rule
from nonebot.typing import T_State
from nonebot_plugin_alconna.uniseg import Hyper, Image, MsgTarget, Reply, Text, UniMessage, UniMsg

from .config import plugin_config
from .content import Column, Dynamic, Video
from .lib.b23_extract import b23_extract
from .lib.content_cd import BilichatCD
from .lib.text_to_image import t2i
from .model.arguments import Options, parser
from .model.exception import AbortError, ProssesError
from .optional import capture_exception

if plugin_config.bilichat_openai_token:
    from .summary import summarization

if plugin_config.bilichat_word_cloud:
    from .wordcloud import wordcloud

lock = asyncio.Lock()


async def _permission_check(bot: Bot, event: Event, target: MsgTarget, state: T_State):
    state["_uid_"] = target.id
    # 自身消息
    _id = target.id if target.private else event.get_user_id()
    if _id == bot.self_id:
        if plugin_config.bilichat_only_self or plugin_config.bilichat_enable_self:
            return True
        elif not plugin_config.bilichat_enable_self:
            return False
    # 不是自身消息但开启了仅自身
    elif plugin_config.bilichat_only_self:
        return False
    # 是否 to me
    if plugin_config.bilichat_only_to_me and not event.is_tome():
        return False
    return plugin_config.verify_permission(target.id)


async def _bili_check(state: T_State, event: Event, bot: Bot, msg: UniMsg) -> bool:
    _msgs = msg.copy()
    if Reply in msg and (
        (plugin_config.bilichat_enable_self and str(event.get_user_id()) == str(bot.self_id)) or event.is_tome()
    ):
        # 如果是回复消息
        # 1. 如果是自身消息且允许自身消息
        # 2. 如果被回复消息中包含对自身的at
        # 满足上述任一条件，则将被回复的消息的内容添加到待解析的内容中
        _msgs.append(Text(str(msg[Reply, 0].msg)))

    bililink = None
    for _msg in _msgs[Text] + _msgs[Hyper]:
        # b23 格式的链接
        _msg_str = str(_msg.data)
        if "b23" in _msg_str:
            if b23 := re.search(r"b23.(tv|wtf)[\\/]+(\w+)", _msg_str):  # type: ignore
                bililink = await b23_extract(list(b23.groups()))
                break
        # av bv cv 格式和动态的链接
        for seg in ("av", "bv", "cv", "dynamic", "opus", "t.bilibili.com"):
            if seg in _msg_str.lower():
                bililink = _msg_str
                break

    if not bililink:
        return False

    content: Column | Video | Dynamic | None = None
    options: Options = state["_options_"]

    try:
        ## video handle
        if matched := re.search(r"(?i)av(\d{1,15})|bv(1[0-9a-z]{9})", bililink):
            _id = matched.group()
            logger.info(f"video id: {_id}")
            content = await Video.from_id(_id, options)

        ## column handle
        elif matched := re.search(r"cv(\d{1,16})", bililink):
            _id = matched.group()
            logger.info(f"column id: {_id}")
            content = await Column.from_id(_id, options)

        ## dynamic handle
        elif plugin_config.bilichat_dynamic and (
            matched := re.search(r"(dynamic|opus|t.bilibili.com)/(\d{1,128})", bililink)
        ):
            _id = matched.group()
            logger.info(f"dynamic id: {_id}")
            content = await Dynamic.from_id(_id)

        if content:
            if options.force:
                BilichatCD.record_cd(state["_uid_"], str(content.id))
            else:
                BilichatCD.check_cd(state["_uid_"], str(content.id))
            state["_content_"] = content
        else:
            raise AbortError(f"查询 {bililink} 返回内容为空")

        return True
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


async def _pre_check(state: T_State, event: Event, bot: Bot, msg: UniMsg, target: MsgTarget):
    set_options(state, msg)
    return await _permission_check(bot, event, target, state) and await _bili_check(state, event, bot, msg)


bilichat = on_message(
    block=plugin_config.bilichat_block,
    priority=2,
    rule=Rule(_pre_check),
)


@bilichat.handle()
async def content_info(event: Event, origin_msg: UniMsg, state: T_State):
    content: Column | Video | Dynamic = state["_content_"]
    reply = Reply(id=origin_msg.get_message_id())
    if plugin_config.bilichat_basic_info:
        content_image = await content.get_image(plugin_config.bilichat_basic_info_style)

        msgs = UniMessage()
        msgs.append(reply)
        if content_image:
            msgs.append(Image(raw=content_image))
        msgs.append(Text(content.url if plugin_config.bilichat_basic_info_url else content.bili_id))
        receipt = await msgs.send()
        reply = receipt.get_reply() or reply if plugin_config.bilichat_reply_to_basic_info else reply

    if not isinstance(content, (Video, Column)):
        return

    future_msg = UniMessage()
    future_msg.append(reply)

    if isinstance(content, Video) and plugin_config.bilichat_official_summary:
        # 获取官方总结内容
        try:
            official_summary_response = await content.get_offical_summary()
            official_summary = official_summary_response.result.markdown()
            try:
                future_msg.append(Image(raw=await t2i(data=official_summary, src="bilibili")))
            except ProssesError:
                future_msg.append(Text(official_summary))
        except Exception as e:
            if not plugin_config.bilichat_summary_ignore_null:
                future_msg.append(Text(f"当前视频不支持AI视频总结: {e}"))
    try:
        async with lock:
            if plugin_config.bilichat_openai_token or plugin_config.bilichat_word_cloud:
                subtitle = await content.get_subtitle()
                if not subtitle:
                    raise AbortError("视频无有效字幕")

                # wordcloud
                if plugin_config.bilichat_word_cloud:
                    if wc_image := await wordcloud(cache=content.cache):
                        future_msg.append(Image(raw=wc_image))

                # summary
                if plugin_config.bilichat_openai_token:
                    if summary := await summarization(cache=content.cache):
                        future_msg.append(Image(raw=summary))

    except FinishedException:
        raise
    except AbortError as e:
        if plugin_config.bilichat_show_error_msg:
            future_msg.append(Text(str(e)))
    except ProssesError as e:
        future_msg.append(Text(str(e)))
    except Exception as e:
        capture_exception()
        logger.exception(e)
        if plugin_config.bilichat_show_error_msg:
            future_msg.append(Text(str(e)))

    if len(future_msg) > 1:
        await future_msg.send()
