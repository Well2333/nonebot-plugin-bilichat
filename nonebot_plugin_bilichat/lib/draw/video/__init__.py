from datetime import datetime
from io import BytesIO

from bilireq.exceptions import ResponseCodeError
from bilireq.grpc.protos.bilibili.app.view.v1.view_pb2 import ViewReply
from httpx import AsyncClient

from ...bilibili_request import get_user_space_info, hc
from ...strings import num_fmt


class UP:
    def __init__(
        self,
        name: str,
        face: bytes | BytesIO,
        level: int,
        fans: str,
        video_counts: int,
        title: str = "UP主",
        name_color: str = "black",
        official_verify: int = -1,
    ) -> None:
        self.name: str = name
        """UP名"""
        self.face: BytesIO = face if isinstance(face, BytesIO) else BytesIO(face)
        """UP头像"""
        self.level: int = level
        """UP等级"""
        self.name_color: str = name_color or "black"
        """UP名字颜色"""
        self.fans: str = fans
        """粉丝数"""
        self.video_counts: int = video_counts
        """视频投稿数量"""
        self.title: str = title
        """合作视频中的角色"""
        self.official_verify: int = official_verify
        """小闪电认证：-1 为无，0 为个人，1 为企业"""

    @classmethod
    async def from_id(cls, client: AsyncClient, mid: int, name: str, title: str):
        try:
            up_data = await get_user_space_info(mid)
        except ResponseCodeError as e:
            if e.code in [-404, 404]:
                up_data = None
            else:
                raise e
        bg_color = up_data["card"]["vip"]["label"]["bg_color"] if up_data else "black"
        level = up_data["card"]["level_info"]["current_level"] if up_data else 0
        video_counts = up_data["archive"]["count"] if up_data else 0
        face_url = up_data["card"]["face"] if up_data else "https://i0.hdslb.com/bfs/face/member/noface.jpg"
        official_verify = up_data["card"]["official_verify"]["type"] if up_data else -1
        face_req = await client.get(face_url)
        if face_req.status_code == 404:
            face_req = await client.get(f"{face_url}@160w_160h_1c_1s.webp")
        face = face_req.content
        return cls(
            name=name,
            name_color=bg_color,
            level=level,
            face=face,
            fans=num_fmt(up_data["card"]["fans"]) if up_data else "N/A",
            video_counts=video_counts,
            title=title,
            official_verify=official_verify,
        )


class VideoImage:
    _render_methods = {}

    def __init__(
        self,
        cover: bytes | BytesIO,
        duration: int,
        type_name: str,
        title: str,
        view: str,
        danmaku: str,
        favorite: str,
        coin: str,
        like: str,
        reply: str,
        share: str,
        pubdate: datetime,
        uploaders: list[UP],
        b23_url: str,
        aid: str,
        desc: str|None = None,
    ):
        self.cover: BytesIO = cover if isinstance(cover, BytesIO) else BytesIO(cover)
        """视频封面"""
        minutes, self.seconds = divmod(duration, 60)
        self.hours, self.minutes = divmod(minutes, 60)
        self.type_name: str = type_name
        """视频分区"""
        self.title: str = title
        """视频标题"""
        self.desc: str = desc or "该视频没有简介"
        """视频简介"""
        self.view: str = view
        """播放量"""
        self.danmaku: str = danmaku
        """弹幕数"""
        self.favorite: str = favorite
        """收藏"""
        self.coin: str = coin
        """投币"""
        self.like: str = like
        """点赞"""
        self.reply: str = reply
        """评论"""
        self.share: str = share
        """分享"""
        self.pubdate: datetime = pubdate
        """发布时间"""
        self.uploaders: list[UP] = uploaders
        """up主列表"""
        self.b23_url: str = b23_url
        """b23短链"""
        self.aid: str = aid
        """av号"""

    @classmethod
    async def from_view_rely(cls, video_view: ViewReply, b23_url: str) -> "VideoImage":
        video_info = video_view.activity_season if video_view.activity_season.arc.aid else video_view
        # 获取封面
        client = hc
        client.headers.update(
            {
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
                    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36"
                ),
                "origin": "https://www.bilibili.com",
                "referer": f"https://www.bilibili.com/video/{video_info.bvid}",
            }
        )
        # 封面
        cover_bytes = (await client.get(video_info.arc.pic)).content
        # up列表
        ups = []
        # 合作视频(UP在第一个)
        if video_info.staff:
            for staff in video_info.staff:
                ups.append(await UP.from_id(client, staff.mid, staff.name, staff.title))
        # 单人视频
        else:
            ups.append(await UP.from_id(client, video_info.arc.author.mid, video_info.arc.author.name, "UP主"))

        return cls(
            cover=cover_bytes,
            duration=video_info.arc.duration,
            type_name=video_info.arc.type_name,
            title=video_info.arc.title,
            desc=video_info.arc.desc,
            view=num_fmt(video_info.arc.stat.view),
            danmaku=num_fmt(video_info.arc.stat.danmaku),
            favorite=num_fmt(video_info.arc.stat.fav),
            coin=num_fmt(video_info.arc.stat.coin),
            like=num_fmt(video_info.arc.stat.like),
            reply=num_fmt(video_info.arc.stat.reply),
            share=num_fmt(video_info.arc.stat.share),
            pubdate=datetime.fromtimestamp(video_info.arc.pubdate),
            uploaders=ups,
            b23_url=b23_url,
            aid=f"av{video_info.arc.aid}",
        )

    @staticmethod
    def get_up_level_code(level: int):
        if level == 0:
            up_level = "\uE6CB"
            level_color = (191, 191, 191)
        elif level == 1:
            up_level = "\uE6CC"
            level_color = (191, 191, 191)
        elif level == 2:
            up_level = "\uE6CD"
            level_color = (149, 221, 178)
        elif level == 3:
            up_level = "\uE6CE"
            level_color = (146, 209, 229)
        elif level == 4:
            up_level = "\uE6CF"
            level_color = (255, 179, 124)
        elif level == 5:
            up_level = "\uE6D0"
            level_color = (255, 108, 0)
        else:
            up_level = "\uE6D1"
            level_color = (255, 0, 0)
        return up_level, level_color

    @classmethod
    def register_method(cls, name=None):
        """
        注册渲染方法的装饰器
        """

        def decorator(func):
            method_name = name or func.__name__
            cls._render_methods[method_name] = func
            return func

        return decorator

    async def render(self, style: str = "bbot_default") -> bytes:
        """
        根据方法名调用已注册的渲染方法
        """
        if style not in self._render_methods:
            raise ValueError(f"No render style registered with the name '{style}'")

        return await self._render_methods[style](self)
