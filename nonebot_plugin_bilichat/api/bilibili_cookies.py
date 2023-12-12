from typing import Dict

from fastapi import HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from nonebot.log import logger

from ..config import plugin_config
from ..lib.bilibili_request.auth import browser_cookies, dump_browser_cookies
from .base import app

# 添加 CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://www.bilibili.com"],
    allow_methods=["POST"],
    allow_headers=["*"],
)


@app.post(f"/{plugin_config.bilichat_webui_url}/api/bili_cookies")
async def receive_cookies(raw_cookies: Dict[str, str]):
    try:
        browser_cookies.update(raw_cookies)
        dump_browser_cookies()
        logger.info("Successfully updated bilibili cookies")
        return Response(status_code=201)
    except Exception as e:
        logger.exception("Failed to update bilibili cookies")
        raise HTTPException(status_code=500, detail=str(e)) from e
