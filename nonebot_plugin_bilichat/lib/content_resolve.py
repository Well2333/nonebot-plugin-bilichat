import time
from typing import Dict, Union

from bilireq.exceptions import GrpcError
from grpc.aio import AioRpcError
from httpx._exceptions import TimeoutException
from nonebot.log import logger

from ..config import plugin_config
from ..model.cache import Cache, Episode
from ..optional import capture_exception  # type: ignore
from .bilibili_request import get_b23_url, grpc_get_view_info
from .draw_bili_image import binfo_image_create
from .video_subtitle import get_subtitle

cd: Dict[str, int] = {}
cd_size_limit = plugin_config.bilichat_cd_time // 2


def check_cd(uid):
    global cd
    now = int(time.time())
    # gc
    if len(cd) > cd_size_limit:
        cd = {k: cd[k] for k in cd if cd[k] < now}
    # check cd
    if cd.get(uid, 0) > now:
        return False
    cd[uid] = now + plugin_config.bilichat_cd_time
    return True


def bv2av(bv):
    table = "fZodR9XQDSUm21yCkr6zBqiveYah8bt4xsWpHnJE7jL5VG3guMTKNPAwcF"
    tr = {table[i]: i for i in range(58)}
    s = [11, 10, 3, 8, 4, 6]
    xor = 177451812
    add = 8728348608
    r = sum(tr[bv[s[i]]] * 58**i for i in range(6))
    return (r - add) ^ xor


async def video_info_get(vid_id: str):
    if vid_id[:2].lower() == "av":
        aid = int(vid_id[2:])
        return await grpc_get_view_info(aid=aid) if aid > 1 else None
    return await grpc_get_view_info(bvid=vid_id)


async def get_video_basic(bili_number: str, uid: Union[str, int]):
    # get video info
    logger.info(f"Parsing video {bili_number}")
    try:
        video_info = await video_info_get(bili_number)
        if not video_info:  # if av is None
            return (None, None, None)
        elif video_info.ecode == 1:
            logger.warning(f"Video {bili_number} not found, might deleted by Uploader")
            return ("未找到此视频，可能已被 UP 主删除。", None, None)
    except Exception as e:
        if isinstance(e, (AioRpcError, GrpcError)):
            capture_exception()
        logger.exception(f"Video message parsing failed, error message: {type(e)} {e}")
        return (f"视频信息解析失败: {type(e)} {e}", None, None)
    aid = video_info.activity_season.arc.aid or video_info.arc.aid
    cid = (
        video_info.activity_season.pages[0].page.cid
        if video_info.activity_season.pages
        else video_info.pages[0].page.cid
    )
    bvid = video_info.activity_season.bvid or video_info.bvid
    title = video_info.activity_season.arc.title or video_info.arc.title

    # check video cd
    if not check_cd(f"{aid}_{uid}"):
        logger.warning(f"Duplicate video {aid}. Skip the video parsing process")
        return (None, None, None)
    # generate video information
    try:
        b23_url = await get_b23_url(f"https://www.bilibili.com/video/{bvid}")
        data = await binfo_image_create(video_info, b23_url)
        logger.debug(f"Video parsing complete - aid:{aid} cid:{cid} title:{title}")
        return (b23_url, data, {"aid": aid, "cid": cid, "title": title})
    except TimeoutException:
        logger.warning("Video parsing API call timeout")
        return (f"{bili_number} 视频信息生成超时，请稍后再试。", None, None)
    except Exception as e:  # noqa
        capture_exception()
        logger.exception(f"Video parsing API call error: {e}")
        return (f"视频解析 API 调用出错：{e}", None, None)


async def get_video_cache(info: Dict):
    # get subtitle
    cache = Cache.get(f'av{info["aid"]}')
    if not cache:
        logger.debug(f'cache of av{info["aid"]} not exists, create cache')
        cache = Cache.create(
            id=f'av{info["aid"]}',
            title=info["title"],
            episodes={
                str(info["cid"]): Episode(
                    title=None,
                    content=await get_subtitle(int(info["aid"]), int(info["cid"])),
                    jieba=None,
                    openai=None,
                )
            },
        )
    elif str(info["cid"]) not in cache.episodes.keys():
        logger.debug(
            f'cache of av{info["aid"]} exists, but cid{info["cid"]} not found, appending cache'
        )
        cache.episodes[str(info["cid"])] = Episode(
            title=None,
            content=await get_subtitle(int(info["aid"]), int(info["cid"])),
            jieba=None,
            openai=None,
        )
    else:
        logger.debug(f'cache of av{info["aid"]} exists, use cache')
    return cache
