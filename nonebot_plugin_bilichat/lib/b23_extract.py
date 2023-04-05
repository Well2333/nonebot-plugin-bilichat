import contextlib
from typing import List

from loguru import logger

from .bilibili_request import hc


async def b23_extract(b23: List[str]):
    try:
        url = f"https://b23.tv/{b23[1]}"
        for _ in range(3):
            with contextlib.suppress(Exception):
                resp = await hc.get(url, follow_redirects=True)
                break
        else:
            return None
        logger.debug(f"b23.tv url: {resp.url}")
        return str(resp.url)
    except TypeError:
        return None
