import asyncio
import re
import time
from typing import Any, Dict, Union

from nonebot.exception import FinishedException
from nonebot.log import logger
from nonebot.typing import T_State

from ..config import plugin_config
from ..content import Column, Dynamic, Video
from ..lib.text_to_image import t2i
from ..model.exception import AbortError

if plugin_config.bilichat_openai_token:
    ENABLE_SUMMARY = True
    from ..summary import summarization
else:
    ENABLE_SUMMARY = False

if plugin_config.bilichat_word_cloud:
    from ..wordcloud.wordcloud import wordcloud

FUTUER_FUCTIONS = ENABLE_SUMMARY or plugin_config.bilichat_word_cloud or plugin_config.bilichat_official_summary


cd: Dict[str, int] = {}
cd_size_limit = plugin_config.bilichat_cd_time // 2
sem = asyncio.Semaphore(1)


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
        logger.warning(f"Duplicate content {id_} from session {session}. Skip the video parsing process")
        raise FinishedException
    elif cd.get(id_, 0) > now:
        logger.warning(f"Duplicate content {id_} from global. Skip the video parsing process")
        raise FinishedException
    else:
        cd[uid] = now + plugin_config.bilichat_cd_time


async def get_content_info_from_state(state: T_State):
    """
    Retrieves information about the content from the given state.

    Args:
        state (T_State): The state object containing the necessary information.

    Returns:
        Union[Column, Video, Dynamic, None]: The content object retrieved from the state.

    Raises:
        AbortError: If the returned content is empty.
    """
    content: Union[Column, Video, Dynamic, None] = None
    ## video handle
    if matched := re.search(r"av(\d{1,15})|BV(1[A-Za-z0-9]{2}4.1.7[A-Za-z0-9]{2})", state["_bililink_"]):
        _id = matched.group()
        logger.info(f"video id: {_id}")
        content = await Video.from_id(_id, state["_options_"])

    ## column handle
    elif matched := re.search(r"cv(\d{1,16})", state["_bililink_"]):
        _id = matched.group()
        logger.info(f"column id: {_id}")
        content = await Column.from_id(_id, state["_options_"])

    ## dynamic handle
    elif plugin_config.bilichat_dynamic and (
        matched := re.search(r"(dynamic|opus|t.bilibili.com)/(\d{1,128})", state["_bililink_"])
    ):
        _id = matched.group()
        logger.info(f"dynamic id: {_id}")
        content = await Dynamic.from_id(_id)

    if content:
        check_cd(f"{state['_uid_']}_-_{content.id}")
        return content
    else:
        raise AbortError(f"查询 {state['_bililink_']} 返回内容为空")


async def get_futuer_fuctions(content: Union[Video, Column, Any]):
    if not (FUTUER_FUCTIONS and content) or not isinstance(content, (Video, Column)):
        raise FinishedException

    official_summary = ""
    wc_image = ""
    summary = ""

    if isinstance(content, Video) and plugin_config.bilichat_official_summary:
        try:
            official_summary_response = await content.get_offical_summary()
            official_summary = await t2i(data=official_summary_response.model_result.markdown(), src="bilibili")
        except Exception as e:
            if plugin_config.bilichat_summary_ignore_null:
                official_summary = ""
            else:
                official_summary = f"当前视频不支持AI视频总结: {e}"

    async with sem:
        if ENABLE_SUMMARY or plugin_config.bilichat_word_cloud:
            subtitle = await content.get_subtitle()
            if not subtitle:
                raise AbortError("视频无有效字幕")

            # wordcloud
            if plugin_config.bilichat_word_cloud:
                wc_image = await wordcloud(cache=content.cache) or ""  # type: ignore

            # summary
            if ENABLE_SUMMARY:
                summary = await summarization(cache=content.cache) or ""  # type: ignore

    return official_summary, wc_image, summary
