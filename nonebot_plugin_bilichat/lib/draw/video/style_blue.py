import base64
import re
from io import BytesIO

import jinja2
from nonebot_plugin_htmlrender.browser import get_new_page
from qrcode.image.pil import PilImage
from qrcode.main import QRCode

from ....config import plugin_config
from ...browser import pw_font_injecter
from ...store import static_dir
from . import VideoImage

style_bule = static_dir.joinpath("style_blue")


@VideoImage.register_method("style_blue")
async def style_blue(video_info: VideoImage):
    video_time = (
        f"{video_info.hours:02d}:{video_info.minutes:02d}:{video_info.seconds:02d}"
        if video_info.hours
        else f"{video_info.minutes:02d}:{video_info.seconds:02d}"
    )
    qr = QRCode(border=1)
    qr.add_data(video_info.b23_url)
    qr_image = BytesIO()
    qr.make_image(PilImage).save(qr_image, "JPEG")

    ups = []
    for up in video_info.uploaders:
        level, level_color = video_info.get_up_level_code(up.level)
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
            "cover_image": f"data:image/png;base64,{base64.b64encode(video_info.cover.getvalue()).decode()}",
            "video_category": video_info.type_name,
            "video_duration": video_time,
            "up_infos": ups,
            "video_title": video_info.title,
            "view_count": video_info.view,
            "dm_count": video_info.danmaku,
            "reply_count": video_info.reply,
            "upload_date": video_info.pubdate.strftime("%Y-%m-%d"),
            "av_number": video_info.aid,
            "video_summary": video_info.desc.replace("\n", "<br>"),
            "like_count": video_info.like,
            "coin_count": video_info.coin,
            "fav_count": video_info.favorite,
            "share_count": video_info.share,
            "qr_code_image": f"data:image/png;base64,{base64.b64encode(qr_image.getvalue()).decode()}",
        }
    )

    async with get_new_page() as page:
        await page.route(re.compile("^https://fonts.bbot/(.+)$"), pw_font_injecter)
        await page.goto(template_path)
        await page.set_content(html, wait_until="networkidle")
        await page.wait_for_timeout(5)
        img_raw = await page.locator(".video").screenshot(
            type="jpeg", quality=plugin_config.bilichat_browser_shot_quality
        )
    return img_raw
