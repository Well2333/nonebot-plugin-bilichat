import asyncio
import re
import time
from typing import Dict, Union

from nonebot.exception import FinishedException
from nonebot.log import logger
from nonebot.typing import T_State

from ..config import plugin_config
from ..content import Column, Video
from ..model.exception import AbortError

INGNORE_TYPE = ("image",)


if plugin_config.bilichat_openai_token or plugin_config.bilichat_newbing_cookie:
    ENABLE_SUMMARY = True
    from ..summary import summarization
else:
    ENABLE_SUMMARY = False

if plugin_config.bilichat_word_cloud:
    from ..wordcloud.wordcloud import wordcloud

INGNORE_TYPE = ("image",)
FUTUER_FUCTIONS = ENABLE_SUMMARY or plugin_config.bilichat_word_cloud


cd: Dict[str, int] = {}
cd_size_limit = plugin_config.bilichat_cd_time // 2
locks = {}


def check_cd(uid: str):
    global cd
    now = int(time.time())
    # gc
    if len(cd) > cd_size_limit:
        cd = {k: cd[k] for k in cd if cd[k] < now}
    # check cd
    if cd.get(uid, 0) > now:
        session, id_ = uid.split("_-_")
        logger.warning(f"Duplicate video(column) {id_} from session {session}. Skip the video parsing process")
        raise FinishedException
    cd[uid] = now + plugin_config.bilichat_cd_time


async def get_content_info_from_state(state: T_State):
    content: Union[Column, Video, None] = None
    try:
        ## video handle
        if matched := re.search(r"av(\d{1,15})|BV(1[A-Za-z0-9]{2}4.1.7[A-Za-z0-9]{2})", state["_bililink_"]):
            content = await Video.from_id(matched.group(), state["_options_"])

        ## column handle
        elif matched := re.search(r"cv(\d{1,16})", state["_bililink_"]):
            content = await Column.from_id(matched.group(), state["_options_"])

        if content:
            check_cd(f"{state['_uid_']}_-_{content.id}")
            return content
        else:
            raise AbortError("返回内容为空")
    except AbortError as e:
        logger.error(e)
        raise FinishedException


async def get_futuer_fuctions(content: Union[Video, Column]):
    global locks
    if not (FUTUER_FUCTIONS and content) or not isinstance(content, (Video, Column)):
        raise FinishedException

    # add lock
    if content.id not in locks:
        locks[content.id] = asyncio.Lock()

    async with locks[content.id]:
        try:
            subtitle = await content.get_subtitle()
            if not subtitle:
                raise AbortError("视频无有效字幕")

            # wordcloud
            wc_image = ""
            if plugin_config.bilichat_word_cloud:
                wc_image = await wordcloud(cache=content.cache) or ""  # type: ignore

            # summary
            summary = ""
            if ENABLE_SUMMARY:
                summary = await summarization(cache=content.cache) or ""  # type: ignore

            return wc_image, summary
        finally:
            if content.id in locks:
                del locks[content.id]
