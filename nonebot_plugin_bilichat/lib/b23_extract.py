import re
import contextlib

from loguru import logger

from .bilibili_request import hc


async def b23_extract(text: str):
    if "b23.tv" not in text and "b23.wtf" not in text:
        return None
    if not (b23 := re.compile(r"b23.(tv|wtf)[\\/]+(\w+)").search(text)):
        return None
    try:
        url = f"https://b23.tv/{b23[2]}"
        for _ in range(3):
            with contextlib.suppress(Exception):
                resp = await hc.get(url, follow_redirects=True)
                break
        else:
            return None
        url = resp.url
        logger.debug(f"b23.tv url: {url}")
        return str(url)
    except TypeError:
        return None
