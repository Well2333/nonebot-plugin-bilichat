from fastapi import APIRouter, HTTPException
from nonebot.log import logger
from pydantic import ValidationError

from nonebot_plugin_bilichat.config import ConfigCTX
from nonebot_plugin_bilichat.model.config import Config
from nonebot_plugin_bilichat.model.subscribe import UserInfo
from nonebot_plugin_bilichat.request_api import init_request_apis
from nonebot_plugin_bilichat.subscribe.fetch_and_push import reset_subs_job

router = APIRouter()


@router.get("/config")
async def get_config() -> Config:
    return ConfigCTX.get()


@router.get("/config/schema")
async def get_config_schema() -> dict:
    return Config.model_json_schema(mode="serialization")


@router.post("/config")
async def set_config(data: Config) -> Config:
    # 检查配置是否合法
    try:
        new_cfg = Config.model_validate(
            data.model_dump(exclude={"version", "webui", "nonebot", "api.local_api_config"})
        )
        old_cfg = ConfigCTX.get()
        new_cfg.version = old_cfg.version
        new_cfg.nonebot = old_cfg.nonebot
        new_cfg.webui = old_cfg.webui
        new_cfg.api.local_api_config = old_cfg.api.local_api_config
        subscribes: dict[str, UserInfo] = {}
        for _id, new_user in new_cfg.subs.users_dict.items():
            if old_user := old_cfg.subs.users_dict.get(_id):
                subscribes[_id] = old_user.model_copy(update={"subscribes": new_user.subscribes_dict})
            else:
                logger.warning(f"User {_id} 不是原有的用户, 忽略")
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=e.json()) from e

    try:
        # 尝试应用配置
        ConfigCTX.set(new_cfg)
        # 重新加载一些配置
        reset_subs_job()
        init_request_apis()
    except Exception as e:
        logger.exception("应用配置失败, 回滚配置")
        ConfigCTX.set(old_cfg)
        raise HTTPException(status_code=400, detail=str(e)) from e

    return ConfigCTX.get()
