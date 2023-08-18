import json
from io import BytesIO
from pathlib import Path
from typing import Dict
from zipfile import ZipFile

from dynamicadaptor.DynamicConversion import formate_message
from httpx import AsyncClient
from minidynamicrender.Core import DyRender
from nonebot.log import logger

from ....config import plugin_config
from ....model.exception import AbortError
from ...fonts_provider import get_font
from ...store import cache_dir, static_dir

# from bilireq.grpc.dynamic import grpc_get_dynamic_detail
# from google.protobuf.json_format import MessageToDict


data_path = cache_dir.joinpath("render")
data_path.mkdir(parents=True, exist_ok=True)
if not data_path.joinpath("Static").exists():
    file = ZipFile(static_dir.joinpath("Static.zip"))
    file.extractall(data_path)
browser_cookies_file = Path(plugin_config.bilichat_bilibili_cookie or "")

# async def pil_dynamic(dynid: str):
#     dynamic: dict = MessageToDict((await grpc_get_dynamic_detail(dynid)).item)
#     dynamic_formate = await formate_message("grpc", dynamic)
#     if dynamic_formate:
#         img_bio = BytesIO()
#         render = DyRender(
#             data_path=str(data_path),
#             font_path={
#                 "text": str(await get_font("HarmonyOS_Sans_SC_Medium.ttf")),
#                 "extra_text": str(await get_font("sarasa-mono-sc-bold.ttf")),
#                 "emoji": str(await get_font("nte.ttf")),
#             },
#         )
#         dynamic_render = await render.dyn_render(dynamic_formate)
#         dynamic_render.convert("RGB").save(img_bio, "jpeg", optimize=True)
#         return img_bio.getvalue()


async def pil_dynamic(dynid: str):
    url = f"https://api.bilibili.com/x/polymer/web-dynamic/v1/detail?timezone_offset=-480&id={dynid}"
    headers = {
        "Referer": f"https://t.bilibili.com/{dynid}",
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36 uacq"
        ),
    }

    cookies = {}
    if browser_cookies_file.exists() and browser_cookies_file.is_file():
        if browser_cookies := json.loads(browser_cookies_file.read_bytes()):
            logger.debug("正在为浏览器添加cookies")
            for cookie in browser_cookies:
                cookies[cookie["name"]] = cookie["value"]
    async with AsyncClient(cookies=cookies) as client:
        resp: Dict = (await client.get(url, headers=headers)).json()
    result = resp.get("data", {}).get("item")
    if not result:
        logger.error(f"Dynamic {dynid} content not correct: {resp}")
        raise AbortError("动态查询信息异常，请查看控制台获取更多信息")
    dynamic_formate = await formate_message("web", result)
    if dynamic_formate:
        img_bio = BytesIO()
        render = DyRender(
            data_path=str(data_path),
            font_path={
                "text": str(await get_font("HarmonyOS_Sans_SC_Medium.ttf")),
                "extra_text": str(await get_font("sarasa-mono-sc-bold.ttf")),
                "emoji": str(await get_font("nte.ttf")),
            },
        )
        dynamic_render = await render.dyn_render(dynamic_formate)
        dynamic_render.convert("RGB").save(img_bio, "jpeg", optimize=True)
        return img_bio.getvalue()
