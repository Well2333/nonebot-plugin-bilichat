import nonebot
from nonebot.compat import model_dump
from nonebot.log import logger
from nonebot_plugin_auto_bot_selector.target import SupportedPlatform
from pydantic import ValidationError

from ..model.api import FaildResponse, Response
from ..model.api.subs_config import Subs
from ..subscribe.manager import SubscriptionSystem
from .base import app

config = nonebot.get_driver().config


@app.get("/api/subs_config")
async def get_subs() -> Response[Subs]:
    return Response[Subs](data=Subs(**SubscriptionSystem.dump_dict()))


@app.put("/api/subs_config")
async def update_subs(data: Subs) -> Response[Subs] | FaildResponse:
    try:
        # 不接收来自前端的 uploaders，由后端自行推导并校验
        await SubscriptionSystem.load(
            model_dump(
                data,
                exclude={
                    "uploaders",
                },
            )
        )
        return Response[Subs](data=Subs(**SubscriptionSystem.dump_dict()))
    except (ValueError, ValidationError) as e:
        return FaildResponse(code=422, message=str(e))
    except Exception as e:
        logger.exception(e)
        return FaildResponse(code=400, message=str(e))


@app.get("/api/subs_config/platform")
async def get_supported_platform() -> Response[list[dict[str, str]]]:
    return Response[list[dict[str, str]]](
        data=[
            {
                "value": SupportedPlatform.qq_group,
                "label": "QQ群",
            },
            {
                "value": SupportedPlatform.qq_guild_channel,
                "label": "QQ频道",
            },
        ]
    )
