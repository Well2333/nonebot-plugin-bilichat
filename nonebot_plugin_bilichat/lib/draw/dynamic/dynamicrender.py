import json
from io import BytesIO
from pathlib import Path
from typing import Dict

import skia
from dynamicadaptor.DynamicConversion import formate_message
from dynrender_skia.Core import DynRender
from httpx import AsyncClient
from nonebot.log import logger

from ....config import plugin_config
from ....model.exception import AbortError
from ...fonts_provider import get_font_sync
from ...store import cache_dir

data_path = cache_dir.joinpath("render")
data_path.mkdir(parents=True, exist_ok=True)
browser_cookies_file = Path(plugin_config.bilichat_bilibili_cookie or "")

render = DynRender(
    static_path=str(data_path),
    font_family=str(get_font_sync("HarmonyOS_Sans_SC_Medium.ttf")),
    emoji_font_family=str(get_font_sync("nte.ttf")),
)


async def skia_dynamic(dynid: str):
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
            logger.debug("正在为添加cookies")
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
        image_array = await render.run(dynamic_formate)
        img = skia.Image.fromarray(image_array, colorType=skia.ColorType.kRGBA_8888_ColorType)
        img.save(img_bio)
        return img_bio.getvalue()
