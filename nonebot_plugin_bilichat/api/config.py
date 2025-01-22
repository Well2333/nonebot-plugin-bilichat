from fastapi import APIRouter, HTTPException
from nonebot.log import logger
from pydantic import ValidationError

from nonebot_plugin_bilichat.config import config, save_config
from nonebot_plugin_bilichat.model.config import Config
from nonebot_plugin_bilichat.model.subscribe import User
from nonebot_plugin_bilichat.request_api import init_request_apis
from nonebot_plugin_bilichat.subscribe.fetch_and_push import reset_subs_job

router = APIRouter()


@router.get("/config")
async def get_config() -> Config:
    return config


@router.post("/config")
async def set_config(data: Config) -> Config:
    global config  # noqa: PLW0603
    # 检查配置是否合法
    try:
        new_cfg = Config.model_validate(
            data.model_dump(exclude={"version", "webui", "nonebot", "api.local_api_config"})
        )
        old_cfg = config.model_copy()
        new_cfg.version = old_cfg.version
        new_cfg.nonebot = old_cfg.nonebot
        new_cfg.webui = old_cfg.webui
        new_cfg.api.local_api_config = old_cfg.api.local_api_config
        subscribes: dict[str, User] = {}
        for _id, new_user in new_cfg.subs.users.items():
            if old_user := old_cfg.subs.users.get(_id):
                subscribes[_id] = old_user.model_copy(update={"subscribes": new_user.subscribes})
            else:
                logger.warning(f"User {_id} 不是原有的用户, 忽略")
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=e.json()) from e

    # 尝试应用配置
    try:
        config = new_cfg
        # 重新加载一些配置
        reset_subs_job()
        init_request_apis()
        # 保存配置
        save_config()
    except Exception as e:
        config = old_cfg
        raise HTTPException(status_code=400, detail=str(e)) from e

    return config
