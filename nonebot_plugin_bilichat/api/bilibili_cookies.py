from typing import Dict

import nonebot
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from nonebot.log import logger

from ..config import plugin_config
from ..lib.bilibili_request.auth import browser_cookies, dump_browser_cookies

if plugin_config.bilichat_bilibili_cookie_api and plugin_config.bilichat_bilibili_cookie:
    config = nonebot.get_driver().config
    logger.info(
        f"Setup bilibili cookies update api at http://{config.host}:{config.port}{plugin_config.bilichat_bilibili_cookie_api}"
    )
    app: FastAPI = nonebot.get_app()

    # 添加 CORS 中间件
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["https://www.bilibili.com"],
        allow_methods=["POST"],
        allow_headers=["*"],
    )

    @app.post(plugin_config.bilichat_bilibili_cookie_api)
    async def receive_cookies(raw_cookies: Dict):
        try:
            browser_cookies.update(raw_cookies)
            dump_browser_cookies()
            logger.info("Successfully updated bilibili cookies")
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e)) from e
        return {"message": "Cookies received successfully"}
