from typing import Dict

import nonebot
from pydantic.error_wrappers import ValidationError

from ..model.api import Response
from ..subscribe.manager import SubscriptionSystem
from .base import app

config = nonebot.get_driver().config


@app.get("/subs_config")
async def get_subs() -> Response:
    return Response(data=SubscriptionSystem.dict())


@app.put("/subs_config")
async def update_subs(data: Dict) -> Response:
    try:
        SubscriptionSystem.load(data)
        return Response(data=SubscriptionSystem.dict())
    except (ValueError, ValidationError) as e:
        return Response(code=422, message=str(e))
    except Exception as e:
        return Response(code=400, message=str(e))
