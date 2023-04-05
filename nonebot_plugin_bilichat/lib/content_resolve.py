from bilireq.exceptions import GrpcError
from grpc.aio import AioRpcError
from httpx._exceptions import TimeoutException
from nonebot.log import logger

from ..optional import capture_exception  # type: ignore
from .bilibili_request import get_b23_url, grpc_get_view_info
from .draw_bili_image import binfo_image_create
from .video_subtitle import get_subtitle
from ..model.cache import Cache, Episode
from typing import Dict


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


async def get_video_basic(bili_number: str):
    # get video info
    try:
        video_info = await video_info_get(bili_number)
        if not video_info:  # if av is None
            return (None, None, None)
        elif video_info.ecode == 1:
            return (f"未找到视频 {bili_number}，可能已被 UP 主删除。", None, None)
    except Exception as e:
        if isinstance(e, (AioRpcError, GrpcError)):
            capture_exception()
        logger.exception(e)
        return (f"{bili_number} 视频信息解析失败，错误信息：{type(e)} {e}", None, None)
    aid = video_info.activity_season.arc.aid or video_info.arc.aid
    cid = (
        video_info.activity_season.pages[0].page.cid
        if video_info.activity_season.pages
        else video_info.pages[0].page.cid
    )
    bvid = video_info.activity_season.bvid or video_info.bvid
    title = video_info.activity_season.arc.title or video_info.arc.title
    # generate video information
    try:
        b23_url = await get_b23_url(f"https://www.bilibili.com/video/{bvid}")
        data = await binfo_image_create(video_info, b23_url)
        return (b23_url, data, {"aid": aid, "cid": cid, "title": title})
    except TimeoutException:
        return (f"{bili_number} 视频信息生成超时，请稍后再试。", None, None)
    except Exception as e:  # noqa
        capture_exception()
        logger.exception("视频解析 API 调用出错")
        return (f"视频解析 API 调用出错：{e}", None, None)


async def get_video_cache(info: Dict):
    # get subtitle
    cache = Cache.get(f'av{info["aid"]}')
    if not cache:
        logger.info(f'cache of av{info["aid"]} not exists, create cache')
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
        logger.info(f'cache of av{info["aid"]} exists, but cid{info["cid"]} not found, appending cache')
        cache.episodes[str(info["cid"])] = Episode(
            title=None,
            content=await get_subtitle(int(info["aid"]), int(info["cid"])),
            jieba=None,
            openai=None,
        )
    else:
        logger.info(f'cache of av{info["aid"]} exists, use cache')
    return cache
