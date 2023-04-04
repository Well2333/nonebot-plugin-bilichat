from io import BytesIO

import qrcode
from bilireq.exceptions import ResponseCodeError
from bilireq.grpc.protos.bilibili.app.view.v1.view_pb2 import ViewReply
from PIL import Image, ImageDraw, ImageFont
from qrcode.image.pil import PilImage

from .bilibili_request import get_user_space_info, hc
from .fonts_provider import get_font_sync
from .strings import get_cut_str, num_fmt

font_semibold = str(get_font_sync("sarasa-mono-sc-semibold.ttf"))
font_bold = str(get_font_sync("sarasa-mono-sc-bold.ttf"))
font_vanfont = str(get_font_sync("vanfont.ttf"))


async def binfo_image_create(video_view: ViewReply, b23_url: str):
    video_info = (
        video_view.activity_season if video_view.activity_season.arc.aid else video_view
    )

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
    bg_y = 0
    # 封面
    pic_url = video_info.arc.pic
    pic_get = (await client.get(pic_url)).content
    pic_bio = BytesIO(pic_get)
    pic = Image.open(pic_bio)
    pic = pic.resize((560, 350))
    pic_time_box = Image.new("RGBA", (560, 50), (0, 0, 0, 150))
    pic.paste(pic_time_box, (0, 300), pic_time_box)
    bg_y += 350 + 20

    # 时长
    minutes, seconds = divmod(video_info.arc.duration, 60)
    hours, minutes = divmod(minutes, 60)
    video_time = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    time_font = ImageFont.truetype(font_bold, 30)
    draw = ImageDraw.Draw(pic)
    draw.text((10, 305), video_time, "white", time_font)

    # 分区
    tname = video_info.arc.type_name
    tname_x, _ = time_font.getsize(tname)
    draw.text((560 - tname_x - 10, 305), tname, "white", time_font)

    # 标题
    title = video_info.arc.title
    title_font = ImageFont.truetype(font_bold, 25)
    title_cut_str = "\n".join(get_cut_str(title, 40))
    _, title_text_y = title_font.getsize_multiline(title_cut_str)
    title_bg = Image.new("RGB", (560, title_text_y + 23), "#F5F5F7")
    draw = ImageDraw.Draw(title_bg)
    draw.text((15, 10), title_cut_str, "black", title_font)
    title_bg_y = title_bg.size[1]
    bg_y += title_bg_y

    # 简介
    desc = video_info.arc.desc
    dynamic = "该视频没有简介" if desc == "" else desc
    dynamic_font = ImageFont.truetype(font_semibold, 18)
    dynamic_cut_str = "\n".join(get_cut_str(dynamic, 58))
    _, dynamic_text_y = dynamic_font.getsize_multiline(dynamic_cut_str)
    dynamic_bg = Image.new("RGB", (560, dynamic_text_y + 24), "#F5F5F7")
    draw = ImageDraw.Draw(dynamic_bg)
    draw.rectangle((0, 0, 580, dynamic_text_y + 24), "#E1E1E5")
    draw.text((10, 10), dynamic_cut_str, "#474747", dynamic_font)
    dynamic_bg_y = dynamic_bg.size[1]
    bg_y += dynamic_bg_y

    # 视频数据
    icon_font = ImageFont.truetype(font_vanfont, 46)
    icon_color = (247, 145, 185)
    info_font = ImageFont.truetype(font_bold, 26)

    view = num_fmt(video_info.arc.stat.view)  # 播放 \uE6E6
    danmaku = num_fmt(video_info.arc.stat.danmaku)  # 弹幕 \uE6E7
    favorite = num_fmt(video_info.arc.stat.fav)  # 收藏 \uE6E1
    coin = num_fmt(video_info.arc.stat.coin)  # 投币 \uE6E4
    like = num_fmt(video_info.arc.stat.like)  # 点赞 \uE6E0

    info_bg = Image.new("RGB", (560, 170), "#F5F5F7")
    draw = ImageDraw.Draw(info_bg)
    draw.text((5 + 10, 20), "\uE6E0", icon_color, icon_font)
    draw.text((5 + 64, 27), like, "#474747", info_font)
    draw.text((5 + 10 + 180, 20), "\uE6E4", icon_color, icon_font)
    draw.text((5 + 64 + 180, 27), coin, "#474747", info_font)
    draw.text((5 + 10 + 180 + 180, 20), "\uE6E1", icon_color, icon_font)
    draw.text((5 + 64 + 180 + 180, 27), favorite, "#474747", info_font)

    draw.text((5 + 100, 93), "\uE6E6", icon_color, icon_font)
    draw.text((5 + 154, 100), view, "#474747", info_font)
    draw.text((5 + 100 + 210, 93), "\uE6E7", icon_color, icon_font)
    draw.text((5 + 154 + 210, 100), danmaku, "#474747", info_font)

    info_bg_y = info_bg.size[1]
    bg_y += info_bg_y

    # UP主
    # 等级 0-4 \uE6CB-F 5-6\uE6D0-1
    # UP \uE723

    up_list = [(x.mid, x.title) for x in video_info.staff if video_info.staff]
    if video_info.arc.author.mid not in [x[0] for x in up_list]:
        up_list.append((video_info.arc.author.mid, "UP主"))
    up_num = len(up_list)
    up_bg = Image.new("RGB", (560, 20 + (up_num * 120) + 20), "#F5F5F7")
    draw = ImageDraw.Draw(up_bg)
    face_size = (80, 80)
    mask = Image.new("RGBA", face_size, color=(0, 0, 0, 0))
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.ellipse((0, 0, face_size[0], face_size[1]), fill=(0, 0, 0, 255))
    name_font = ImageFont.truetype(font_bold, 24)
    up_title_font = ImageFont.truetype(font_bold, 20)
    follower_font = ImageFont.truetype(font_semibold, 22)

    for i, up in enumerate(up_list):
        uid, up_title = up
        try:
            up_data = await get_user_space_info(uid)
        except ResponseCodeError as e:
            if e.code in [-404, 404]:
                up_data = None
            else:
                raise e
        name_color = up_data["card"]["vip"]["label"]["bg_color"] if up_data else "black"

        current_level = up_data["card"]["level_info"]["current_level"] if up_data else 0
        if current_level == 0:
            up_level = "\uE6CB"
            level_color = (191, 191, 191)
        elif current_level == 1:
            up_level = "\uE6CC"
            level_color = (191, 191, 191)
        elif current_level == 2:
            up_level = "\uE6CD"
            level_color = (149, 221, 178)
        elif current_level == 3:
            up_level = "\uE6CE"
            level_color = (146, 209, 229)
        elif current_level == 4:
            up_level = "\uE6CF"
            level_color = (255, 179, 124)
        elif current_level == 5:
            up_level = "\uE6D0"
            level_color = (255, 108, 0)
        else:
            up_level = "\uE6D1"
            level_color = (255, 0, 0)

        # 头像
        face_url = (
            up_data["card"]["face"]
            if up_data
            else "https://i0.hdslb.com/bfs/face/member/noface.jpg"
        )
        face_req = await client.get(face_url)
        if face_req.status_code == 404:
            face_req = await client.get(f"{face_url}@160w_160h_1c_1s.webp")
        face_get = face_req.content
        face_bio = BytesIO(face_get)
        face = Image.open(face_bio)
        face.convert("RGB")
        face = face.resize(face_size)
        up_bg.paste(face, (20, 20 + (i * 120)), mask)
        # 名字
        draw.text(
            (160, 25 + (i * 120)),
            up_data["card"]["name"] if up_data else f"账号已注销（{uid}）",
            name_color or "black",
            name_font,
        )
        name_size_x, _ = name_font.getsize(
            up_data["card"]["name"] if up_data else f"账号已注销（{uid} "
        )
        # 等级
        draw.text(
            (160 + name_size_x + 10, 16 + (i * 120)), up_level, level_color, icon_font
        )
        # 身份
        up_title_size_x, up_title_size_y = up_title_font.getsize(up_title)
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
        draw.text((67, 13 + (i * 120)), up_title, icon_color, up_title_font)
        # 粉丝量
        draw.text(
            (162, 66 + (i * 120)),
            "粉丝 " + num_fmt(up_data["card"]["fans"]) if up_data else "N/A",
            "#474747",
            follower_font,
        )
    up_bg_y = up_bg.size[1]
    bg_y += up_bg_y - 18

    # 底部栏
    banner_bg = Image.new("RGB", (600, 170), icon_color)
    draw = ImageDraw.Draw(banner_bg)
    # 二维码
    qr = qrcode.QRCode(border=1)
    qr.add_data(b23_url)
    qr_image = qr.make_image(PilImage, fill_color=icon_color, back_color="#F5F5F7")
    qr_image = qr_image.resize((140, 140))
    banner_bg.paste(qr_image, (50, 10))
    # Logo
    # LOGO \uE725
    logo_font = ImageFont.truetype(font_vanfont, 100)
    draw.text((300, 28), "\uE725", "#F5F5F7", logo_font)
    bg_y += 170

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
