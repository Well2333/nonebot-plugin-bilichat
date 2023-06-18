import time
from typing import Dict, Union

from bilireq.exceptions import GrpcError
from grpc.aio import AioRpcError
from httpx._exceptions import TimeoutException
from nonebot.log import logger

from ..config import plugin_config
from ..model.arguments import Options
from ..model.cache import Cache, Episode
from ..model.content import Video, Column
from ..model.exception import AbortError
from ..optional import capture_exception  # type: ignore
from .bilibili_request import get_b23_url, grpc_get_view_info
from .draw_bili_image import BiliVideoImage
from .video_subtitle import get_subtitle
from .column_resolve import get_cv


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
        data = (
            (await (await BiliVideoImage.from_view_rely(video_info, b23_url)).render(plugin_config.bilichat_basic_info_style))
            if plugin_config.bilichat_basic_info
            else "IMG_RENDER_DISABLED"
        )
        logger.debug(f"Video parsing complete - aid:{aid} cid:{cid} title:{title}")
        return (b23_url, data, Video(aid, cid, title))
    except TimeoutException:
        logger.warning("Video parsing API call timeout")
        return (f"{bili_number} 视频信息生成超时，请稍后再试。", None, None)
    except Exception as e:  # noqa
        capture_exception()
        logger.exception(f"Video parsing API call error: {e}")
        return (f"视频解析 API 调用出错：{e}", None, None)


async def get_column_basic(bili_number: str, uid: Union[str, int]):
    try:
        if not check_cd(f"{bili_number}_{uid}"):
            logger.warning(f"Duplicate column {bili_number}. Skip the video parsing process")
            return None
        cvid = bili_number[2:]
        cv_title, cv_text = await get_cv(cvid)
        return Column(int(cvid), cv_title, cv_text)
    except AbortError:
        logger.warning("Column not found, might deleted by Uploader")
        return "未找到此专栏，可能已被 UP 主删除。"
    except TimeoutException:
        logger.warning("Column parsing API call timeout")
        return f"{bili_number} 专栏信息生成超时，请稍后再试。"
    except Exception as e:  # noqa
        capture_exception()
        logger.exception(f"Column parsing API call error: {e}")
        return f"专栏解析 API 调用出错：{e}"


async def get_content_cache(info: Union[Video, Column], options: Options):
    async def create_cache():
        return Cache.create(
            id=f"{id_}",
            title=info.title,
            episodes={
                str(info.cid): Episode(
                    title=None,
                    content=await get_subtitle(int(info.aid), int(info.cid)) if isinstance(info, Video) else info.text,
                    jieba=None,
                    openai=None,
                    newbing=None,
                )
            },
            temp=options.no_cache,
        )

    if isinstance(info, Video):
        id_ = f"av{info.aid}"
    elif isinstance(info, Column):
        id_ = f"cv{info.aid}"
    else:
        raise ValueError(f"unkown type of content {info}")

    if options.no_cache:
        logger.debug(f"parameter --no-cache of {id_} detected, using temporary cache")
        return await create_cache()

    cache = Cache.get(id_)
    # cache file not exists
    if not cache:
        logger.debug(f"cache of {id_} not exists, create cache")
        return await create_cache()
    # cache file exists but cid not found
    elif str(info.cid) not in cache.episodes.keys():
        logger.debug(f"cache of {id_} exists, but cid{info.cid} not found, appending cache")
        cache.episodes[str(info.cid)] = Episode(
            title=None,
            content=await get_subtitle(int(info.aid), int(info.cid)) if isinstance(info, Video) else info.text,
            jieba=None,
            openai=None,
            newbing=None,
        )
    # all exists but need refresh
    elif options.refresh:
        logger.debug(f"parameter --refresh of {id_} detected, remove summary cache")
        episode = cache.episodes[str(info.cid)]
        episode.jieba = None
        episode.openai = None
        episode.newbing = None
    # all exists
    else:
        logger.debug(f"cache of {id_} exists, use cache")
    return cache
