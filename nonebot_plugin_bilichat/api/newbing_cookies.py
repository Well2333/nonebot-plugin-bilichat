import json
from pathlib import Path

import nonebot
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from nonebot.log import logger

from ..config import plugin_config

if (
    plugin_config.bilichat_newbing_cookie_api
    and plugin_config.bilichat_newbing_cookie
    and plugin_config.bilichat_newbing_cookie != "no_login"
):
    config = nonebot.get_driver().config
    logger.info(
        f"Setup newbing cookies update api at http://{config.host}:{config.port}{plugin_config.bilichat_newbing_cookie_api}"
    )
    cookies_file = Path(plugin_config.bilichat_newbing_cookie)
    app: FastAPI = nonebot.get_app()

    # 添加 CORS 中间件
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["https://www.bing.com"],
        allow_methods=["POST"],
        allow_headers=["*"],
    )

    @app.post(plugin_config.bilichat_newbing_cookie_api)
    async def receive_cookies(raw_cookies: dict):
        try:
            cookies = [
                {"domain": ".bing.com", "name": name, "path": "/", "value": value}
                for name, value in raw_cookies.items()
            ]
            cookies_file.write_text(json.dumps(cookies))
            logger.info("Successfully updated newbing cookies")
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e)) from e
        return {"message": "Cookies received successfully"}
