import asyncio
from io import BytesIO

from PIL import Image, ImageDraw, ImageFont
from qrcode.image.pil import PilImage
from qrcode.main import QRCode

from ...strings import get_cut_str
from .. import font_bold, font_semibold, font_vanfont
from . import VideoImage


def getsize(info_str: str, font):
    box = ImageDraw.Draw(Image.new("RGB", (1000, 1000))).multiline_textbbox(xy=(0, 0), text=info_str, font=font)
    width = box[2] - box[0]
    height = box[3] - box[1]
    return width, height


@VideoImage.register_method("bbot_default")
async def bbot_default_async(video_info: VideoImage):
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, bbot_default, video_info)


def bbot_default(video_info: VideoImage):
    bg_y = 0
    # ===  封面 ===
    ## 封面
    cover = Image.open(video_info.cover)
    pic = cover.resize((560, 350))
    pic_time_box = Image.new("RGBA", (560, 50), (0, 0, 0, 150))
    pic.paste(pic_time_box, (0, 300), pic_time_box)
    bg_y += 350 + 20
    ## 时长
    video_time = f"{video_info.hours:02d}:{video_info.minutes:02d}:{video_info.seconds:02d}"
    time_font = ImageFont.truetype(font_bold, 30)
    draw = ImageDraw.Draw(pic)
    draw.text((10, 305), video_time, "white", time_font)
    ## 分区
    tname = video_info.type_name
    tname_x, _ = getsize(tname, time_font)
    draw.text((560 - tname_x - 10, 305), tname, "white", time_font)

    # === 标题 ===
    title_font = ImageFont.truetype(font_bold, 25)
    title_cut_str = "\n".join(get_cut_str(video_info.title, 40))
    _, title_text_y = getsize(title_cut_str, title_font)
    title_bg = Image.new("RGB", (560, title_text_y + 23), "#F5F5F7")
    draw = ImageDraw.Draw(title_bg)
    draw.text((15, 10), title_cut_str, "black", title_font)
    title_bg_y = title_bg.size[1]
    bg_y += title_bg_y

    # === 简介 ===
    dynamic = video_info.desc
    dynamic_font = ImageFont.truetype(font_semibold, 18)
    dynamic_cut_str = "\n".join(get_cut_str(dynamic, 58))
    _, dynamic_text_y = getsize(dynamic_cut_str, dynamic_font)
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
    draw.text((5 + 64, 27), video_info.like, "#474747", info_font)
    ## 投币
    draw.text((5 + 10 + 180, 20), "\uE6E4", icon_color, icon_font)
    draw.text((5 + 64 + 180, 27), video_info.coin, "#474747", info_font)
    ## 收藏
    draw.text((5 + 10 + 180 + 180, 20), "\uE6E1", icon_color, icon_font)
    draw.text((5 + 64 + 180 + 180, 27), video_info.favorite, "#474747", info_font)
    ## 播放
    draw.text((5 + 100, 93), "\uE6E6", icon_color, icon_font)
    draw.text((5 + 154, 100), video_info.view, "#474747", info_font)
    ## 弹幕
    draw.text((5 + 100 + 210, 93), "\uE6E7", icon_color, icon_font)
    draw.text((5 + 154 + 210, 100), video_info.danmaku, "#474747", info_font)
    #
    info_bg_y = info_bg.size[1]
    bg_y += info_bg_y

    # UP主
    # 等级 0-4 \uE6CB-F 5-6\uE6D0-1
    # UP \uE723
    up_num = len(video_info.uploaders)
    up_bg = Image.new("RGB", (560, 20 + (up_num * 120) + 20), "#F5F5F7")
    draw = ImageDraw.Draw(up_bg)
    face_size = (80, 80)
    mask = Image.new("RGBA", face_size, color=(0, 0, 0, 0))
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.ellipse((0, 0, face_size[0], face_size[1]), fill=(0, 0, 0, 255))
    name_font = ImageFont.truetype(font_bold, 24)
    up_title_font = ImageFont.truetype(font_bold, 20)
    follower_font = ImageFont.truetype(font_semibold, 22)
    for i, up in enumerate(video_info.uploaders):
        up_level, level_color = video_info.get_up_level_code(up.level)
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
        name_size_x, _ = getsize(up.name, name_font)
        # 等级
        draw.text((160 + name_size_x + 10, 16 + (i * 120)), up_level, level_color, icon_font)
        # 身份
        up_title_size_x, up_title_size_y = getsize(up.title, up_title_font)
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
    qr = QRCode(border=1)
    qr.add_data(video_info.b23_url)
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
