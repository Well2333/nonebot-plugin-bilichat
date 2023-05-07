import re
import shlex
from itertools import chain
from typing import cast

from nonebot.adapters import MessageSegment
from nonebot.adapters.onebot.v11 import GroupMessageEvent as V11_GME
from nonebot.adapters.onebot.v11 import PrivateMessageEvent as V11_PME
from nonebot.adapters.onebot.v12 import GroupMessageEvent as V12_GME
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
from .lib.content_resolve import get_column_basic, get_content_cache, get_video_basic
from .model.arguments import Options, parser
from .model.exception import AbortError
from .optional import capture_exception  # type: ignore
from .utils import BOT, MESSAGE_EVENT, get_image, get_reply

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
    extra={
        "author": "djkcyl & Well404",
        "version": __version__,
        "priority": 1,
    },
)


async def _bili_check(bot: BOT, event: MESSAGE_EVENT, state: T_State):
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
async def get_bili_number_re(state: T_State):
    state["bili_number"] = state[REGEX_STR]


@b23.handle()
async def get_bili_number_b23(state: T_State):
    bililink = await b23_extract(state[REGEX_GROUP])
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
    reply = await get_reply(event)
    # basic info
    bili_number, uid = state["bili_number"], state["_uid_"]
    if bili_number[:2] in ["BV", "bv", "av"]:
        msg, img, info = await get_video_basic(bili_number, uid)
        if not msg or not info:
            raise FinishedException
        if not img:
            await matcher.finish(reply + msg)
        elif img != "IMG_RENDER_DISABLED":
            image = await get_image(img, bot)
            msgid = (await matcher.send(reply + image + msg))["message_id"]  # type: ignore
            if plugin_config.bilichat_reply_to_basic_info:
                reply = await get_reply(event, msgid)
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
        await matcher.finish(f"{reply}视频字幕获取失败: {str(e)}")
    except Exception as e:
        capture_exception()
        logger.exception(e)
        await matcher.finish(f"{reply}未知错误: {e}")

    # wordcloud
    wc_image = ""
    if plugin_config.bilichat_word_cloud:
        if image := await wordcloud(cache=cache, cid=str(info.cid)):
            wc_image = await get_image(image, bot)
        else:
            await matcher.finish(f"{reply}视频无有效字幕")

    # summary
    summary = ""
    if ENABLE_SUMMARY:
        if summary := await summarization(cache=cache, cid=str(info.cid)):
            if isinstance(summary, bytes):
                summary = await get_image(summary, bot)
        else:
            await matcher.finish(f"{reply}视频无有效字幕")

    if wc_image or summary:
        await matcher.finish(reply + wc_image + summary)  # type: ignore
