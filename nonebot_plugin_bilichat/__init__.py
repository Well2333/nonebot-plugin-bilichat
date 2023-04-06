import re
from typing import Union

from nonebot.adapters.onebot.v11 import GroupMessageEvent as V11_GME
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
from nonebot.log import logger
from nonebot.matcher import Matcher
from nonebot.plugin import PluginMetadata, on_regex
from nonebot.rule import Rule
from nonebot.typing import T_State

from .config import __version__, plugin_config
from .lib.b23_extract import b23_extract
from .lib.content_resolve import get_video_basic, get_video_cache
from .lib.content_summarise import openai_summarization
from .lib.wordcloud import wordcloud
from .model.exception import AbortError
from .optional import capture_exception

__plugin_meta__ = PluginMetadata(
    name="nonebot-plugin-bilichat",
    description="一个通过 OpenAI 来对b站视频进行总结插件",
    usage="直接发送视频链接即可",
    extra={
        "author": "djkcyl",
        "version": __version__,
        "priority": 1,
    },
)


async def _bili_check(event: Union[V11_ME, V12_ME], state: T_State):
    if isinstance(event, (V11_PME, V12_PME)):
        state["_uid_"] = event.user_id
        return plugin_config.bilichat_enable_private
    elif isinstance(event, (V11_GME, V12_GME)):
        state["_uid_"] = event.group_id
        return plugin_config.verify_permission(event.group_id)
    elif isinstance(event, V12_CME):
        state["_uid_"] = event.channel_id
        return plugin_config.bilichat_enable_v12_channel
    else:
        state["_uid_"] = "unkown"
        return plugin_config.bilichat_enable_unkown_src


bili = on_regex(
    r"av(\d{1,15})|BV(1[A-Za-z0-9]{2}4.1.7[A-Za-z0-9]{2})",
    block=plugin_config.bilichat_block,
    priority=1,
    rule=Rule(_bili_check),  # type: ignore
)


@bili.handle()
async def get_bili_number_re(state: T_State):
    state["bili_number"] = state[REGEX_STR]


b23 = on_regex(
    r"b23.(tv|wtf)[\\/]+(\w+)",
    block=plugin_config.bilichat_block,
    priority=1,
    rule=Rule(_bili_check),  # type: ignore
)


@b23.handle()
async def get_bili_number_b23(state: T_State):
    if matched := re.search(r"av(\d{1,15})|BV(1[A-Za-z0-9]{2}4.1.7[A-Za-z0-9]{2})", await b23_extract(state[REGEX_GROUP])):  # type: ignore
        state["bili_number"] = matched.group()


@bili.handle()
@b23.handle()
async def video_info_v11(event: V11_ME, state: T_State, matcher: Matcher):
    # basic info
    msg, img, info = await get_video_basic(state["bili_number"], state["_uid_"])
    if not msg or not info:
        await matcher.finish()
    reply = V11_MS.reply(event.message_id)
    if not img:
        await matcher.finish(reply + msg)
    image = V11_MS.image(img)
    msgid = (await matcher.send(reply + image + msg))["message_id"]
    # furtuer fuctions
    if plugin_config.bilichat_openai_token or plugin_config.bilichat_word_cloud:
        reply = V11_MS.reply(msgid)
        try:
            cache = await get_video_cache(info)
        except AbortError as e:
            logger.exception(e)
            await matcher.finish(reply + "视频字幕获取失败: " + str(e))  # type: ignore
        except Exception as e:
            capture_exception()
            logger.exception(e)
            await matcher.finish(reply + "未知错误: " + str(e))  # type: ignore
        if plugin_config.bilichat_word_cloud:
            await matcher.send(
                reply + V11_MS.image(await wordcloud(cache=cache, cid=str(info["cid"])))  # type: ignore
            )
        if plugin_config.bilichat_openai_token:
            await matcher.send(reply + await openai_summarization(cache=cache, cid=str(info["cid"])))  # type: ignore


@bili.handle()
@b23.handle()
async def video_info_v12(bot: V12_Bot, event: V12_ME, state: T_State, matcher: Matcher):
    # basic info
    msg, img, info = await get_video_basic(state["bili_number"], state["_uid_"])
    if not msg:
        await matcher.finish()
    reply = V12_MS.reply(event.message_id)
    if not img:
        await matcher.finish(reply + msg)
    fileid = await bot.upload_file(
        type="data", name=f"{state['bili_number']}.jpg", data=img
    )
    image = V12_MS.image(file_id=fileid["file_id"])
    msgid = (await matcher.send(reply + image + msg))["message_id"]
    # furtuer fuctions
    if plugin_config.bilichat_openai_token or plugin_config.bilichat_word_cloud:
        reply = V12_MS.reply(msgid)
        try:
            cache = await get_video_cache(info)  # type: ignore
        except AbortError as e:
            logger.exception(e)
            await matcher.finish(reply + "视频字幕获取失败: " + str(e))  # type: ignore
        except Exception as e:
            capture_exception()
            logger.exception(e)
            await matcher.finish(reply + "未知错误: " + str(e))  # type: ignore
        if plugin_config.bilichat_word_cloud:
            fileid = await bot.upload_file(
                type="data", name=f"{state['bili_number']}_wc.jpg", data=await wordcloud(cache=cache, cid=str(info["cid"]))  # type: ignore
            )
            await matcher.send(reply + V12_MS.image(file_id=fileid["file_id"]))
        if plugin_config.bilichat_openai_token:
            await matcher.send(reply + await openai_summarization(cache=cache, cid=str(info["cid"])))  # type: ignore
