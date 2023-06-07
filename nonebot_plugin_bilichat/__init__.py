import contextlib
import re
import shlex
from itertools import chain
from typing import Tuple, Union, cast

from nonebot.adapters import MessageSegment
from nonebot.adapters.mirai2 import Bot as Mirai_Bot
from nonebot.adapters.mirai2.event import FriendMessage as Mirai_PME
from nonebot.adapters.mirai2.event import GroupMessage as Mirai_GME
from nonebot.adapters.mirai2.event import MessageEvent as Mirai_ME
from nonebot.adapters.onebot.v11 import Bot as V11_Bot
from nonebot.adapters.onebot.v11 import GroupMessageEvent as V11_GME
from nonebot.adapters.onebot.v11 import MessageEvent as V11_ME
from nonebot.adapters.onebot.v11 import PrivateMessageEvent as V11_PME
from nonebot.adapters.onebot.v12 import Bot as V12_Bot
from nonebot.adapters.onebot.v12 import ChannelMessageEvent as V12_CME
from nonebot.adapters.onebot.v12 import GroupMessageEvent as V12_GME
from nonebot.adapters.onebot.v12 import MessageEvent as V12_ME
from nonebot.adapters.onebot.v12 import PrivateMessageEvent as V12_PME
from nonebot.adapters.qqguild import Bot as QG_Bot
from nonebot.adapters.qqguild.event import MessageEvent as QG_ME
from nonebot.exception import FinishedException
from nonebot.log import logger
from nonebot.matcher import Matcher
from nonebot.params import Depends, RegexGroup, RegexStr
from nonebot.plugin import PluginMetadata, on_regex, require
from nonebot.rule import Rule
from nonebot.typing import T_State

from .config import __version__, plugin_config
from .lib.b23_extract import b23_extract
from .lib.content_resolve import get_column_basic, get_content_cache, get_video_basic
from .model.arguments import Options, parser
from .model.exception import AbortError
from .optional import capture_exception  # type: ignore

require("nonebot_plugin_segbuilder")


from nonebot_plugin_segbuilder import SegmentBuilder

BOT = Union[V11_Bot, V12_Bot, QG_Bot, Mirai_Bot]
MESSAGE_EVENT = Union[V11_ME, V12_ME, QG_ME, Mirai_ME]

if plugin_config.bilichat_openai_token or plugin_config.bilichat_newbing_cookie:
    ENABLE_SUMMARY = True
    from .summary import summarization
else:
    ENABLE_SUMMARY = False

if plugin_config.bilichat_word_cloud:
    from .wordcloud.wordcloud import wordcloud

FUTUER_FUCTIONS = ENABLE_SUMMARY or plugin_config.bilichat_word_cloud

__plugin_meta__ = PluginMetadata(
    name="nonebot-plugin-bilichat",
    description="一个通过 OpenAI 来对b站视频进行总结插件",
    usage="直接发送视频链接即可",
    homepage="https://github.com/Aunly/nonebot-plugin-bilichat",
    type="application",
    supported_adapters={"~onebot.v11", "~onebot.v12", "~qqguild", "~mirai2"},
    extra={
        "author": "djkcyl & Well404",
        "version": __version__,
        "priority": 1,
    },
)


async def _bili_check(bot: BOT, event: MESSAGE_EVENT, state: T_State):
    # check if self msg
    if str(event.get_user_id()) == str(bot.self_id):
        if plugin_config.bilichat_only_self:
            state["_uid_"] = event.get_session_id()
            return True
        elif not plugin_config.bilichat_enable_self:
            return False
    elif plugin_config.bilichat_only_self:
        return False
    # private msg use user id
    if isinstance(event, (V11_PME, V12_PME, Mirai_PME)):
        state["_uid_"] = event.get_user_id()
        return plugin_config.bilichat_enable_private
    # group msg use group id
    elif isinstance(event, (V11_GME, V12_GME)):
        state["_uid_"] = event.group_id
        return plugin_config.verify_permission(event.group_id)
    elif isinstance(event, Mirai_GME):
        state["_uid_"] = event.sender.group.id
        return plugin_config.verify_permission(event.sender.group.id)
    # channel like msg use channel id
    elif isinstance(event, (V12_CME, QG_ME)):
        state["_uid_"] = event.channel_id
        return plugin_config.bilichat_enable_channel
    # other
    else:
        state["_uid_"] = "unkown"
        return plugin_config.bilichat_enable_unkown_src


bili = on_regex(
    r"av(\d{1,15})|BV(1[A-Za-z0-9]{2}4.1.7[A-Za-z0-9]{2})|cv(\d{1,16})",
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


def get_args(event: MESSAGE_EVENT):
    return parser.parse_known_args(
        list(
            chain.from_iterable(
                shlex.split(str(seg)) if cast(MessageSegment, seg).is_text() else (seg,) for seg in event.get_message()
            )
        ),  # type: ignore
        namespace=Options(),
    )[0]


@bili.handle()
async def get_bili_number_re(state: T_State, bili_number: str = RegexStr()):
    state["bili_number"] = bili_number


@b23.handle()
async def get_bili_number_b23(state: T_State, b23: Tuple = RegexGroup()):
    bililink = await b23_extract(list(b23))
    if matched := re.search(
        r"av(\d{1,15})|BV(1[A-Za-z0-9]{2}4.1.7[A-Za-z0-9]{2})|cv(\d{1,16})", bililink  # type: ignore
    ):
        state["bili_number"] = matched.group()
    else:
        logger.info(f"{bililink} is not video or column")
        raise FinishedException


@bili.handle()
@b23.handle()
async def video_info(
    bot: BOT,
    event: MESSAGE_EVENT,
    state: T_State,
    matcher: Matcher,
    options: Options = Depends(get_args),
):
    # sourcery skip: raise-from-previous-error, use-fstring-for-concatenation
    DISABLE_REPLY = isinstance(bot, Mirai_Bot)  # 部分平台Reply暂不可用
    DISABLE_LINK = isinstance(bot, QG_Bot) or not plugin_config.bilichat_basic_info_url  # 部分平台发送链接都要审核
    SEND_IMAGE_SEPARATELY = isinstance(bot, QG_Bot)  # 部分平台无法一次性发送多张图片，或无法与其他消息组合发出
    reply = "" if DISABLE_REPLY else await SegmentBuilder.reply()
    # basic info
    bili_number, uid = state["bili_number"], state["_uid_"]
    if bili_number[:2] in ["BV", "bv", "av"]:
        msg, img, info = await get_video_basic(bili_number, uid)
        if not msg or not info:
            raise FinishedException
        if not img:
            await matcher.finish(reply + msg)
        elif img != "IMG_RENDER_DISABLED":
            image = await SegmentBuilder.image(image=img)
            msg = "" if DISABLE_LINK else msg
            if SEND_IMAGE_SEPARATELY:
                if reply and msg:
                    await matcher.send(reply + msg)
                re_msg = await matcher.send(image)
            else:
                re_msg = await matcher.send(reply + image + msg)
            if plugin_config.bilichat_reply_to_basic_info and not DISABLE_REPLY:
                with contextlib.suppress(Exception):
                    reply = await SegmentBuilder.reply(message_id=re_msg["message_id"])
    elif bili_number[:2] == "cv" and FUTUER_FUCTIONS:
        info = await get_column_basic(bili_number, uid)
        if not info:
            raise FinishedException
        elif isinstance(info, str):
            await matcher.finish(reply + info)
    else:
        raise FinishedException

    # furtuer fuctions
    if not FUTUER_FUCTIONS:
        raise FinishedException

    # get video cache
    try:
        cache = await get_content_cache(info, options)
    except AbortError as e:
        logger.exception(e)
        if plugin_config.bilichat_show_error_msg:
            await matcher.finish(reply + f"视频字幕获取失败: {str(e)}")
        raise FinishedException
    except Exception as e:
        capture_exception()
        logger.exception(e)
        if plugin_config.bilichat_show_error_msg:
            await matcher.finish(reply + f"未知错误: {e}")
        raise FinishedException

    # wordcloud
    wc_image = ""
    if plugin_config.bilichat_word_cloud:
        if image := await wordcloud(cache=cache, cid=str(info.cid)):
            wc_image = await SegmentBuilder.image(image=image)
            if SEND_IMAGE_SEPARATELY:
                await matcher.send(wc_image)
        else:
            if plugin_config.bilichat_show_error_msg:
                await matcher.finish(reply + "视频无有效字幕")
            raise FinishedException

    # summary
    summary = ""
    if ENABLE_SUMMARY:
        if summary := await summarization(cache=cache, cid=str(info.cid)):
            # if summary is image
            if isinstance(summary, bytes):
                summary = await SegmentBuilder.image(image=summary)
            if SEND_IMAGE_SEPARATELY:
                await matcher.finish(summary)
        else:
            if plugin_config.bilichat_show_error_msg:
                await matcher.finish(reply + "视频无有效字幕")
            raise FinishedException

    if (not SEND_IMAGE_SEPARATELY) and (wc_image or summary):
        await matcher.finish(reply + wc_image + summary)
