import time
from typing import Dict, Union

from bilireq.exceptions import GrpcError
from grpc.aio import AioRpcError
from httpx._exceptions import TimeoutException
from lxml import etree
from lxml.etree import _Element, _ElementUnicodeResult
from nonebot.log import logger

from ..config import plugin_config
from ..model.arguments import Options
from ..model.cache import Cache, Episode
from ..model.content import Column, Video
from ..model.exception import AbortError, SkipProssesException
from .bilibili_request import get_b23_url, grpc_get_view_info, hc
from .draw_bili_image import BiliVideoImage
from .video_subtitle import get_subtitle

XPATH = "//p//text() | //h1/text() | //h2/text() | //h3/text() | //h4/text() | //h5/text() | //h6/text()"

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
        logger.warning(f"Duplicate video(column) {uid}. Skip the video parsing process")
        raise SkipProssesException(f"Duplicate video(column) {uid}. Skip the video parsing process")
    cd[uid] = now + plugin_config.bilichat_cd_time


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
    # sourcery skip: raise-from-previous-error
    # get video info
    logger.info(f"Parsing video {bili_number}")
    try:
        video_info = await video_info_get(bili_number)
        if not video_info or video_info.ecode == 1:
            logger.warning(f"Video {bili_number} not found, might deleted by Uploader")
            raise AbortError("未找到此视频，可能不存在或已被删除。")
    except Exception as e:
        logger.exception(f"Video message parsing failed, error message: {type(e)} {e}")
        raise AbortError(f"视频信息解析失败: {type(e)} {e}") from e

    aid = video_info.activity_season.arc.aid or video_info.arc.aid
    cid = (
        video_info.activity_season.pages[0].page.cid
        if video_info.activity_season.pages
        else video_info.pages[0].page.cid
    )
    bvid = video_info.activity_season.bvid or video_info.bvid
    title = video_info.activity_season.arc.title or video_info.arc.title

    # check video cd
    check_cd(f"{aid}_{uid}")
    # generate video information
    try:
        b23_url = await get_b23_url(f"https://www.bilibili.com/video/{bvid}")
        data = (
            (
                await (await BiliVideoImage.from_view_rely(video_info, b23_url)).render(
                    plugin_config.bilichat_basic_info_style
                )
            )
            if plugin_config.bilichat_basic_info
            else "IMG_RENDER_DISABLED"
        )
        logger.debug(f"Video parsing complete - aid:{aid} cid:{cid} title:{title}")
        return (b23_url, data, Video(aid, cid, title))
    except TimeoutException:
        logger.warning("Video parsing API call timeout")
        raise AbortError(f"{bili_number} 视频信息生成超时，请稍后再试。")
    except Exception as e:  # noqa
        logger.exception(f"Video parsing API call error: {e}")
        raise AbortError("视频解析 API 调用出错") from e


async def get_column_basic(bili_number: str, uid: Union[str, int]):
    # sourcery skip: raise-from-previous-error
    check_cd(f"{bili_number}_{uid}")
    try:
        cvid = bili_number[2:]
        cv = await hc.get(f"https://www.bilibili.com/read/cv{cvid}")
        if cv.status_code != 200:
            raise AbortError("未找到此专栏，可能已被 UP 主删除。")
        cv.encoding = "utf-8"
        cv = cv.text
        http_parser: _Element = etree.fromstring(cv, etree.HTMLParser(encoding="utf-8"))
        cv_title: str = http_parser.xpath('//h1[@class="title"]/text()')[0]
        main_article: _Element = http_parser.xpath('//div[@id="read-article-holder"]')[0]
        plist: _ElementUnicodeResult = main_article.xpath(XPATH)
        cv_text = [text.strip() for text in plist if text.strip()]

        return Column(int(cvid), cv_title, cv_text)
    except TimeoutException:
        logger.warning("Column parsing API call timeout")
        raise AbortError(f"{bili_number} 专栏信息生成超时，请稍后再试。")
    except Exception as e:  # noqa
        logger.exception(f"Column parsing API call error: {e}")
        raise AbortError(f"专栏解析 API 调用出错：{e}") from e


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
