import re
import shlex
from itertools import chain
from typing import Union, cast

from nonebot.adapters import MessageSegment
from nonebot.adapters.onebot.v11 import Bot as V11_Bot
from nonebot.adapters.onebot.v11 import GroupMessageEvent as V11_GME
from nonebot.adapters.onebot.v11 import Message as V11_Message
from nonebot.adapters.onebot.v11 import MessageEvent as V11_ME
from nonebot.adapters.onebot.v11 import MessageSegment as V11_MS
from nonebot.adapters.onebot.v11 import PrivateMessageEvent as V11_PME
from nonebot.adapters.onebot.v12 import Bot as V12_Bot
from nonebot.adapters.onebot.v12 import ChannelMessageEvent as V12_CME
from nonebot.adapters.onebot.v12 import GroupMessageEvent as V12_GME
from nonebot.adapters.onebot.v12 import MessageEvent as V12_ME
from nonebot.adapters.onebot.v12 import MessageSegment as V12_MS
from nonebot.adapters.onebot.v12 import PrivateMessageEvent as V12_PME
from nonebot.consts import REGEX_GROUP, REGEX_STR
from nonebot.exception import FinishedException
from nonebot.log import logger
from nonebot.matcher import Matcher
from nonebot.params import Depends
from nonebot.plugin import PluginMetadata, on_regex
from nonebot.rule import Rule
from nonebot.typing import T_State

from .config import __version__, plugin_config
from .lib.b23_extract import b23_extract
from .lib.content_resolve import get_video_basic, get_video_cache
from .model.arguments import Options, parser
from .model.exception import AbortError
from .optional import capture_exception  # type: ignore

if plugin_config.bilichat_openai_token or plugin_config.bilichat_newbing_cookie:
    ENABLE_SUMMARY = True
    from .summary import summarization
else:
    ENABLE_SUMMARY = False

if plugin_config.bilichat_word_cloud:
    from .wordcloud.wordcloud import wordcloud

__plugin_meta__ = PluginMetadata(
    name="nonebot-plugin-bilichat",
    description="一个通过 OpenAI 来对b站视频进行总结插件",
    usage="直接发送视频链接即可",
    extra={
        "author": "djkcyl & Well404",
        "version": __version__,
        "priority": 1,
    },
)


async def _bili_check(bot: Union[V11_Bot, V12_Bot], event: Union[V11_ME, V12_ME], state: T_State):
    if str(event.get_user_id()) == str(bot.self_id):
        return plugin_config.bilichat_enable_self
    elif isinstance(event, (V11_PME, V12_PME)):
        state["_uid_"] = event.user_id
        return plugin_config.bilichat_enable_private
    elif isinstance(event, (V11_GME, V12_GME)):
        state["_uid_"] = event.group_id
        return plugin_config.verify_permission(event.group_id)
    # elif isinstance(event, V12_CME):
    #     state["_uid_"] = event.channel_id
    #     return plugin_config.bilichat_enable_v12_channel
    else:
        state["_uid_"] = "unkown"
        return plugin_config.bilichat_enable_unkown_src


bili = on_regex(
    r"av(\d{1,15})|BV(1[A-Za-z0-9]{2}4.1.7[A-Za-z0-9]{2})",
    block=plugin_config.bilichat_block,
    priority=1,
    rule=Rule(_bili_check),
)

b23 = on_regex(
    r"b23.(tv|wtf)[\\/]+(\w+)",
    block=plugin_config.bilichat_block,
    priority=1,
    rule=Rule(_bili_check),
)


def get_args(event: Union[V11_ME, V12_ME]):
    return parser.parse_known_args(
        list(
            chain.from_iterable(
                shlex.split(str(seg)) if cast(MessageSegment, seg).is_text() else (seg,) for seg in event.get_message()
            )
        ),  # type: ignore
        namespace=Options(),
    )[0]


@bili.handle()
async def get_bili_number_re(state: T_State):
    state["bili_number"] = state[REGEX_STR]


@b23.handle()
async def get_bili_number_b23(state: T_State):
    if matched := re.search(
        r"av(\d{1,15})|BV(1[A-Za-z0-9]{2}4.1.7[A-Za-z0-9]{2})", await b23_extract(state[REGEX_GROUP])  # type: ignore
    ):
        state["bili_number"] = matched.group()


@bili.handle()
@b23.handle()
async def video_info_v11(
    bot: V11_Bot, event: V11_ME, state: T_State, matcher: Matcher, options: Options = Depends(get_args)
):
    # sourcery skip: raise-from-previous-error
    # basic info
    msg, img, info = await get_video_basic(state["bili_number"], state["_uid_"])
    if not msg or not info:
        await matcher.finish()
    reply = V11_MS.reply(event.message_id)
    if not img:
        await matcher.finish(reply + msg)
    elif img != "IMG_RENDER_DISABLED":
        image = V11_MS.image(img)
        msgid = (await matcher.send(reply + image + msg))["message_id"]
        if plugin_config.bilichat_reply_to_basic_info:
            reply = V11_MS.reply(msgid)

    # furtuer fuctions
    if not ENABLE_SUMMARY and not plugin_config.bilichat_word_cloud:
        raise FinishedException

    # get video cache
    try:
        cache = await get_video_cache(info, options)
    except AbortError as e:
        logger.exception(e)
        await matcher.finish(f"{reply}视频字幕获取失败: {str(e)}")
    except Exception as e:
        capture_exception()
        logger.exception(e)
        await matcher.finish(f"{reply}未知错误: {e}")

    # wordcloud
    wc_image = ""
    if plugin_config.bilichat_word_cloud:
        if image := await wordcloud(cache=cache, cid=str(info["cid"])):
            wc_image = V11_MS.image(image)
        else:
            await matcher.finish(f"{reply}视频无有效字幕")

    # summary
    summary = ""
    if ENABLE_SUMMARY:
        if summary := await summarization(cache=cache, cid=str(info["cid"])):
            if isinstance(summary, bytes):
                summary = V11_MS.image(summary)
        else:
            await matcher.finish(f"{reply}视频无有效字幕")

    if wc_image or summary:
        await matcher.finish(reply + wc_image + summary)


async def get_image_v12(bot: V12_Bot, bili_number: str, suffix: str, data):
    fileid = await bot.upload_file(type="data", name=f"{bili_number}_{suffix}.jpg", data=data)
    return V12_MS.image(file_id=fileid["file_id"])


@bili.handle()
@b23.handle()
async def video_info_v12(
    bot: V12_Bot, event: V12_ME, state: T_State, matcher: Matcher, options: Options = Depends(get_args)
):
    # basic info
    msg, img, info = await get_video_basic(state["bili_number"], state["_uid_"])
    if not msg:
        await matcher.finish()
    reply = V12_MS.reply(message_id=event.message_id, user_id=event.get_user_id())
    if not img or not info:
        await matcher.finish(reply + msg)
    elif img != "IMG_RENDER_DISABLED":
        image = await get_image_v12(bot, state["bili_number"], suffix="basic", data=img)
        msgid = (await matcher.send(reply + image + msg))["message_id"]
        if plugin_config.bilichat_reply_to_basic_info:
            reply = V12_MS.reply(msgid)

    # furtuer fuctions
    if not ENABLE_SUMMARY and not plugin_config.bilichat_word_cloud:
        raise FinishedException

    try:
        cache = await get_video_cache(info, options)
    except AbortError as e:
        logger.exception(e)
        await matcher.finish(f"{reply}视频字幕获取失败: {str(e)}")
    except Exception as e:
        capture_exception()
        logger.exception(e)
        await matcher.finish(f"{reply}未知错误: {str(e)}")

    # wordcloud
    wc_image = ""
    if plugin_config.bilichat_word_cloud:
        if image := await wordcloud(cache=cache, cid=str(info["cid"])):
            wc_image = await get_image_v12(bot, state["bili_number"], "wc", data=image)
        else:
            await matcher.send(f"{reply}视频无有效字幕")

    # summary
    summary = ""
    if ENABLE_SUMMARY:
        if summary := await summarization(cache=cache, cid=str(info["cid"])):
            if isinstance(summary, bytes):
                summary = await get_image_v12(bot, state["bili_number"], "summary", data=summary)
        else:
            await matcher.send(f"{reply}视频无有效字幕")

    if wc_image or summary:
        await matcher.finish(reply + wc_image + summary)  # type: ignore
