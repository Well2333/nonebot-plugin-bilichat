import asyncio
import base64
import re
from datetime import datetime
from io import BytesIO
from pathlib import Path
from typing import List, Optional, Union

import qrcode
from bilireq.exceptions import ResponseCodeError
from bilireq.grpc.protos.bilibili.app.view.v1.view_pb2 import ViewReply
from httpx import AsyncClient
from PIL import Image, ImageDraw, ImageFont
from qrcode.image.pil import PilImage

from .bilibili_request import get_user_space_info, hc
from .fonts_provider import get_font_sync
from .strings import get_cut_str, num_fmt

font_semibold = str(get_font_sync("sarasa-mono-sc-semibold.ttf"))
font_bold = str(get_font_sync("sarasa-mono-sc-bold.ttf"))
font_vanfont = str(get_font_sync("vanfont.ttf"))


class UP:
    def __init__(
        self,
        name: str,
        face: Union[bytes, BytesIO],
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


class BiliVideoImage:
    def __init__(
        self,
        cover: Union[bytes, BytesIO],
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
        uploaders: List[UP],
        b23_url: str,
        aid: str,
        desc: Optional[str] = None,
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
        self.uploaders: List[UP] = uploaders
        """up主列表"""
        self.b23_url: str = b23_url
        """b23短链"""
        self.aid: str = aid
        """av号"""

    @classmethod
    async def from_view_rely(cls, video_view: ViewReply, b23_url: str) -> "BiliVideoImage":
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

    async def render(self, style: str = "bbot_default"):
        loop = asyncio.get_running_loop()
        if style == "bbot_default":
            return await loop.run_in_executor(None, self.style_bbot_default)  # type: ignore
        if style == "style_blue":
            return await self.style_blue()

    def style_bbot_default(self):
        bg_y = 0
        # ===  封面 ===
        ## 封面
        cover = Image.open(self.cover)
        pic = cover.resize((560, 350))
        pic_time_box = Image.new("RGBA", (560, 50), (0, 0, 0, 150))
        pic.paste(pic_time_box, (0, 300), pic_time_box)
        bg_y += 350 + 20
        ## 时长
        video_time = f"{self.hours:02d}:{self.minutes:02d}:{self.seconds:02d}"
        time_font = ImageFont.truetype(font_bold, 30)
        draw = ImageDraw.Draw(pic)
        draw.text((10, 305), video_time, "white", time_font)
        ## 分区
        tname = self.type_name
        tname_x, _ = time_font.getsize(tname)
        draw.text((560 - tname_x - 10, 305), tname, "white", time_font)

        # === 标题 ===
        title_font = ImageFont.truetype(font_bold, 25)
        title_cut_str = "\n".join(get_cut_str(self.title, 40))
        _, title_text_y = title_font.getsize_multiline(title_cut_str)
        title_bg = Image.new("RGB", (560, title_text_y + 23), "#F5F5F7")
        draw = ImageDraw.Draw(title_bg)
        draw.text((15, 10), title_cut_str, "black", title_font)
        title_bg_y = title_bg.size[1]
        bg_y += title_bg_y

        # === 简介 ===
        dynamic = self.desc
        dynamic_font = ImageFont.truetype(font_semibold, 18)
        dynamic_cut_str = "\n".join(get_cut_str(dynamic, 58))
        _, dynamic_text_y = dynamic_font.getsize_multiline(dynamic_cut_str)
        dynamic_bg = Image.new("RGB", (560, dynamic_text_y + 24), "#F5F5F7")
        draw = ImageDraw.Draw(dynamic_bg)
        draw.rectangle((0, 0, 580, dynamic_text_y + 24), "#E1E1E5")
        draw.text((10, 10), dynamic_cut_str, "#474747", dynamic_font)
        dynamic_bg_y = dynamic_bg.size[1]
        bg_y += dynamic_bg_y

        # === 视频数据 ===
        icon_font = ImageFont.truetype(font_vanfont, 46)
        icon_color = (247, 145, 185)
        info_font = ImageFont.truetype(font_bold, 26)
        info_bg = Image.new("RGB", (560, 170), "#F5F5F7")
        draw = ImageDraw.Draw(info_bg)
        ## 点赞
        draw.text((5 + 10, 20), "\uE6E0", icon_color, icon_font)
        draw.text((5 + 64, 27), self.like, "#474747", info_font)
        ## 投币
        draw.text((5 + 10 + 180, 20), "\uE6E4", icon_color, icon_font)
        draw.text((5 + 64 + 180, 27), self.coin, "#474747", info_font)
        ## 收藏
        draw.text((5 + 10 + 180 + 180, 20), "\uE6E1", icon_color, icon_font)
        draw.text((5 + 64 + 180 + 180, 27), self.favorite, "#474747", info_font)
        ## 播放
        draw.text((5 + 100, 93), "\uE6E6", icon_color, icon_font)
        draw.text((5 + 154, 100), self.view, "#474747", info_font)
        ## 弹幕
        draw.text((5 + 100 + 210, 93), "\uE6E7", icon_color, icon_font)
        draw.text((5 + 154 + 210, 100), self.danmaku, "#474747", info_font)
        #
        info_bg_y = info_bg.size[1]
        bg_y += info_bg_y

        # UP主
        # 等级 0-4 \uE6CB-F 5-6\uE6D0-1
        # UP \uE723
        up_num = len(self.uploaders)
        up_bg = Image.new("RGB", (560, 20 + (up_num * 120) + 20), "#F5F5F7")
        draw = ImageDraw.Draw(up_bg)
        face_size = (80, 80)
        mask = Image.new("RGBA", face_size, color=(0, 0, 0, 0))
        mask_draw = ImageDraw.Draw(mask)
        mask_draw.ellipse((0, 0, face_size[0], face_size[1]), fill=(0, 0, 0, 255))
        name_font = ImageFont.truetype(font_bold, 24)
        up_title_font = ImageFont.truetype(font_bold, 20)
        follower_font = ImageFont.truetype(font_semibold, 22)
        for i, up in enumerate(self.uploaders):
            up_level, level_color = self.get_up_level_code(up.level)
            # 头像
            face = Image.open(up.face)
            face.convert("RGB")
            face = face.resize(face_size)
            up_bg.paste(face, (20, 20 + (i * 120)), mask)
            # 名字
            draw.text(
                (160, 25 + (i * 120)),
                up.name,
                up.name_color,
                name_font,
            )
            name_size_x, _ = name_font.getsize(up.name)
            # 等级
            draw.text((160 + name_size_x + 10, 16 + (i * 120)), up_level, level_color, icon_font)
            # 身份
            up_title_size_x, up_title_size_y = up_title_font.getsize(up.title)
            draw.rectangle(
                (
                    60,
                    10 + (i * 120),
                    73 + up_title_size_x,
                    18 + (i * 120) + up_title_size_y,
                ),
                "white",
                icon_color,
                3,
            )
            draw.text((67, 13 + (i * 120)), up.title, icon_color, up_title_font)
            # 粉丝量
            draw.text((162, 66 + (i * 120)), f"粉丝 {up.fans}", "#474747", follower_font)

        # === UP ===
        up_bg_y = up_bg.size[1]
        bg_y += up_bg_y - 18
        # 底部栏
        banner_bg = Image.new("RGB", (600, 170), icon_color)
        draw = ImageDraw.Draw(banner_bg)
        # 二维码
        qr = qrcode.QRCode(border=1)
        qr.add_data(self.b23_url)
        qr_image = qr.make_image(PilImage, fill_color=icon_color, back_color="#F5F5F7")
        qr_image = qr_image.resize((140, 140))
        banner_bg.paste(qr_image, (50, 10))
        # Logo
        # LOGO \uE725
        logo_font = ImageFont.truetype(font_vanfont, 100)
        draw.text((300, 28), "\uE725", "#F5F5F7", logo_font)
        bg_y += 170

        # === 汇总 ===
        video = Image.new("RGB", (600, bg_y + 40), "#F5F5F7")
        video.paste(pic, (20, 20))
        video.paste(title_bg, (20, 390))
        video.paste(dynamic_bg, (20, 390 + title_bg_y + 20))
        video.paste(info_bg, (20, 390 + title_bg_y + 20 + dynamic_bg_y + 20))
        video.paste(up_bg, (20, 390 + title_bg_y + 20 + dynamic_bg_y + 10 + info_bg_y))
        video.paste(
            banner_bg,
            (0, 390 + title_bg_y + 20 + dynamic_bg_y + 10 + info_bg_y + up_bg_y - 18),
        )
        image = BytesIO()
        video.save(image, "JPEG")

        return image.getvalue()

    async def style_blue(self):
        import jinja2
        from nonebot_plugin_htmlrender.browser import get_new_page

        from ..lib.browser import pw_font_injecter

        style_bule = Path(__file__).parent.parent.joinpath("static", "style_blue")
        video_time = (
            f"{self.hours:02d}:{self.minutes:02d}:{self.seconds:02d}"
            if self.hours
            else f"{self.minutes:02d}:{self.seconds:02d}"
        )
        qr = qrcode.QRCode(border=1)
        qr.add_data(self.b23_url)
        qr_image = BytesIO()
        qr.make_image(PilImage).save(qr_image, "JPEG")

        ups = []
        for up in self.uploaders:
            level, level_color = self.get_up_level_code(up.level)
            info = {
                "avatar_image": f"data:image/png;base64,{base64.b64encode(up.face.getvalue()).decode()}",
                "name": up.name,
                "level": level,
                "name_color": up.name_color,
                "level_color": f"rgba{level_color}",
                "fans_count": up.fans,
                "video_count": up.video_counts,
                "icon": up.official_verify,
                "condition": up.title,
            }
            ups.append(info)

        template_env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(style_bule),
            enable_async=True,
        )
        template_path = f"file:///{style_bule.joinpath('video-details.html').absolute()}".replace("////", "///")
        template = template_env.get_template("video-details.html")
        html = await template.render_async(
            **{
                "cover_image": f"data:image/png;base64,{base64.b64encode(self.cover.getvalue()).decode()}",
                "video_category": self.type_name,
                "video_duration": video_time,
                "up_infos": ups,
                "video_title": self.title,
                "view_count": self.view,
                "dm_count": self.danmaku,
                "reply_count": self.reply,
                "upload_date": self.pubdate.strftime("%Y-%m-%d"),
                "av_number": self.aid,
                "video_summary": self.desc.replace("\n", "<br>"),
                "like_count": self.like,
                "coin_count": self.coin,
                "fav_count": self.favorite,
                "share_count": self.share,
                "qr_code_image": f"data:image/png;base64,{base64.b64encode(qr_image.getvalue()).decode()}",
            }
        )

        async with get_new_page() as page:
            await page.route(re.compile("^https://fonts.bbot/(.+)$"), pw_font_injecter)
            await page.goto(template_path)
            await page.set_content(html, wait_until="networkidle")
            await page.wait_for_timeout(5)
            img_raw = await page.locator(".video").screenshot(
                type="png",
            )
        return img_raw
