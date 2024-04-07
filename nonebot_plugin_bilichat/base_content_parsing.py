import asyncio
import re
import time
from typing import Dict, Union

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
from .lib.text_to_image import t2i
from .model.arguments import Options
from .model.exception import AbortError, ProssesError
from .optional import capture_exception

if plugin_config.bilichat_openai_token:
    from .summary import summarization

if plugin_config.bilichat_word_cloud:
    from .wordcloud import wordcloud

cd: Dict[str, int] = {}
cd_size_limit = plugin_config.bilichat_cd_time // 2

# 临时解决方案
try:
    lock = asyncio.Lock()
except RuntimeError:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    lock = asyncio.Lock(loop=loop)  # type: ignore


def check_cd(uid: Union[int, str], check: bool = True):
    global cd
    now = int(time.time())
    uid = str(uid)
    # gc
    if len(cd) > cd_size_limit:
        cd = {k: cd[k] for k in cd if cd[k] < now}
    # not check cd
    if not check:
        cd[uid] = now + plugin_config.bilichat_cd_time
        return
    # check cd
    session, id_ = uid.split("_-_")
    if cd.get(uid, 0) > now:
        logger.warning(f"会话 [{session}] 的重复内容 [{id_}]. 跳过解析")
        raise FinishedException
    elif cd.get(id_, 0) > now:
        logger.warning(f"会话 [全局] 的重复内容 [{id_}]. 跳过解析")
        raise FinishedException
    else:
        cd[uid] = now + plugin_config.bilichat_cd_time


async def _permission_check(bot: Bot, event: Event, target: MsgTarget, state: T_State):
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
    state["_uid_"] = target.id
    return plugin_config.verify_permission(target.id)


async def _bili_check(state: T_State, event: Event, bot: Bot, msg: UniMsg) -> bool:
    # 检查并提取 raw_bililink
    try:
        if plugin_config.bilichat_enable_self and str(event.get_user_id()) == str(bot.self_id) and (Reply in msg):
            # 是自身消息的情况下，检查是否是回复，是的话则取被回复的消息
            _msgs = UniMessage(msg[Reply, 0].msg) or msg
        else:
            _msgs = msg
    except Exception:
        _msgs = msg

    bililink = None
    for _msg in _msgs[Text] + _msgs[Hyper]:
        # b23 格式的链接
        _msg_str = str(_msg)
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

    content: Union[Column, Video, Dynamic, None] = None
    options = Options()

    try:
        ## video handle
        if matched := re.search(r"av(\d{1,15})|BV(1[A-Za-z0-9]{2}4.1.7[A-Za-z0-9]{2})", bililink):
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
            check_cd(f"{state['_uid_']}_-_{content.id}")
            state["_content_"] = content
        else:
            raise AbortError(f"查询 {bililink} 返回内容为空")

        return True
    except AbortError as e:
        logger.info(e)
        return False
    except FinishedException:
        return False


async def _pre_check(state: T_State, event: Event, bot: Bot, msg: UniMsg, target: MsgTarget):
    return await _permission_check(bot, event, target, state) and await _bili_check(state, event, bot, msg)


bilichat = on_message(
    block=plugin_config.bilichat_block,
    priority=1,
    rule=Rule(_pre_check),
)


@bilichat.handle()
async def content_info(event: Event, origin_msg: UniMsg, state: T_State):
    content: Union[Column, Video, Dynamic] = state["_content_"]
    reply = Reply(id=origin_msg.get_message_id())
    if plugin_config.bilichat_basic_info:
        content_image = await content.get_image(plugin_config.bilichat_basic_info_style)

        msgs = UniMessage()
        msgs.append(reply)
        if content_image:
            msgs.append(Image(raw=content_image))
        msgs.append(content.url if plugin_config.bilichat_basic_info_url else content.bili_id)
        receipt = await msgs.send()
        reply = receipt.get_reply() if plugin_config.bilichat_reply_to_basic_info else reply

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
