from typing import Dict

from fastapi import HTTPException, Response
from nonebot.log import logger

from ..lib.bilibili_request.auth import browser_cookies, dump_browser_cookies
from .base import app


@app.post("/bili_cookies")
async def receive_cookies(raw_cookies: Dict[str, str]):
    try:
        browser_cookies.update(raw_cookies)
        dump_browser_cookies()
        logger.info("Successfully updated bilibili cookies")
        return Response(status_code=201)
    except Exception as e:
        logger.exception("Failed to update bilibili cookies")
        raise HTTPException(status_code=500, detail=str(e)) from e
