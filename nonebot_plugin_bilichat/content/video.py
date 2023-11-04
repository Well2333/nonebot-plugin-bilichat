from typing import Optional

from bilireq.grpc.protos.bilibili.app.view.v1.view_pb2 import ViewReply
from bilireq.utils import get
from nonebot.log import logger
from pydantic import BaseModel, ValidationError

from ..lib.bilibili_request import get_b23_url, grpc_get_view_info
from ..lib.cache import BaseCache, Cache
from ..lib.draw import VideoImage
from ..lib.video_subtitle import get_subtitle
from ..model.arguments import Options
from ..model.bilibili.summary import SummaryApiResponse
from ..model.exception import AbortError
from ..optional import capture_exception


class Video(BaseModel):
    id: int
    """视频av号"""
    title: str
    """视频标题"""
    url: str
    """b23 链接"""
    raw: ViewReply
    """原始信息"""
    cache: BaseCache

    class Config:
        arbitrary_types_allowed = True

    @property
    def bili_id(self) -> str:
        return f"av{self.id}"

    @classmethod
    async def from_id(cls, bili_number: str, options: Optional[Options] = None):
        logger.info(f"Parsing video {bili_number}")
        video_info = None
        if bili_number[:2].lower() == "av":
            if aid := int(bili_number[2:]):
                video_info = await grpc_get_view_info(aid=aid)
        else:
            video_info = await grpc_get_view_info(bvid=bili_number)
        try:
            if not video_info or video_info.ecode == 1:
                raise AbortError("未找到此视频，可能不存在或已被删除。")
        except Exception as e:
            raise AbortError(f"视频信息解析失败: {type(e)} {e}") from e

        aid = video_info.activity_season.arc.aid or video_info.arc.aid
        title = video_info.activity_season.arc.title or video_info.arc.title
        b23_url = await get_b23_url(f"https://www.bilibili.com/video/av{aid}")

        if options:
            if options.no_cache:
                logger.debug(f"parameter --no-cache of av{aid} detected, using temporary cache")
                cache = BaseCache(id=f"av{aid}", title=title)
            elif options.refresh:
                logger.debug(f"parameter --refresh of av{aid} detected, remove cache")
                cache = Cache(id=f"av{aid}", title=title)
                await cache.save()
            else:
                cache = await Cache.load(f"av{aid}", title=title)
        else:
            cache = await Cache.load(f"av{aid}", title=title)

        content = cls(id=aid, title=title, url=b23_url, raw=video_info, cache=cache)
        return content

    async def get_subtitle(self):
        cid = (
            self.raw.activity_season.pages[0].page.cid if self.raw.activity_season.pages else self.raw.pages[0].page.cid
        )
        if self.cache.content:
            logger.debug(f"subtitle cache of av{self.id} exists, use cache")
        else:
            logger.debug(f"subtitle cache of av{self.id} not exists")
            subtitle = await get_subtitle(aid=self.id, cid=cid)
            self.cache.content = subtitle
            await self.cache.save()
        return self.cache.content

    async def get_image(self, style: str):
        return await (await VideoImage.from_view_rely(self.raw, self.url)).render(style)

    async def get_offical_summary(self):
        resp = await get(
            "https://api.bilibili.com/x/web-interface/view/conclusion/get",
            params={
                "bvid": self.raw.bvid,
                "cid": self.raw.activity_season.pages[0].page.cid
                if self.raw.activity_season.pages
                else self.raw.pages[0].page.cid,
                "up_mid": self.raw.arc.author.mid,
                "web_location": "0.0",
            },
            is_wbi=True,
        )
        logger.debug(resp)
        try:
            summary = SummaryApiResponse(**resp)
        except ValidationError as e:
            capture_exception(extra={"response": resp})
            raise AbortError("获取官方视频总结失败") from e
        return summary
