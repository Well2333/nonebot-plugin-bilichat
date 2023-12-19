from typing import Union

import nonebot
from pydantic.error_wrappers import ValidationError

from ..model.api import FaildResponse
from ..model.api.subs_config import Subs, SubsResponse
from ..subscribe.manager import SubscriptionSystem
from .base import app

config = nonebot.get_driver().config


@app.get("/subs_config")
async def get_subs() -> SubsResponse:
    return SubsResponse(data=Subs(**SubscriptionSystem.dict()))


@app.put("/subs_config")
async def update_subs(data: Subs) -> Union[SubsResponse, FaildResponse]:
    try:
        SubscriptionSystem.load(data.dict())
        return SubsResponse(data=Subs(**SubscriptionSystem.dict()))
    except (ValueError, ValidationError) as e:
        return FaildResponse(code=422, message=str(e))
    except Exception as e:
        return FaildResponse(code=400, message=str(e))
