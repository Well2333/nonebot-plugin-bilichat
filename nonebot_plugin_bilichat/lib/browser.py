from nonebot.log import logger
from playwright.async_api._generated import Request, Route
from yarl import URL

from .fonts_provider import get_font

font_mime_map = {
    "collection": "font/collection",
    "otf": "font/otf",
    "sfnt": "font/sfnt",
    "ttf": "font/ttf",
    "woff": "font/woff",
    "woff2": "font/woff2",
}


async def pw_font_injecter(route: Route, request: Request):
    url = URL(request.url)
    if not url.is_absolute():
        raise ValueError("字体地址不合法")
    try:
        logger.debug(f"Font {url.query['name']} requested")
        await route.fulfill(
            path=await get_font(url.query["name"]),
            content_type=font_mime_map.get(url.suffix),
        )
        return
    except Exception:
        logger.error(f"找不到字体 {url.query['name']}")
        await route.fallback()
