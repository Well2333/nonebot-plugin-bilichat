from typing import Dict

import nonebot
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse

from ..config import plugin_config
from ..subscribe.manager import SubscriptionSystem

config = nonebot.get_driver().config
app: FastAPI = nonebot.get_app()


@app.get(f"/{plugin_config.bilichat_webui_url}/api/config")
async def get_subs():
    return JSONResponse(SubscriptionSystem.dict())


@app.put(f"/{plugin_config.bilichat_webui_url}/api/config")
async def update_subs(data: Dict):
    try:
        SubscriptionSystem.load(data)
        return JSONResponse(SubscriptionSystem.dict())
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
