from typing import Dict

import nonebot
from fastapi import HTTPException
from fastapi.responses import JSONResponse

from ..subscribe.manager import SubscriptionSystem
from .base import app

config = nonebot.get_driver().config


@app.get("/subs_config")
async def get_subs():
    return JSONResponse(SubscriptionSystem.dict())


@app.put("/subs_config")
async def update_subs(data: Dict):
    try:
        SubscriptionSystem.load(data)
        return JSONResponse(SubscriptionSystem.dict())
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
