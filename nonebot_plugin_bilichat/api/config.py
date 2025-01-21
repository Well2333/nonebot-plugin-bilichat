from fastapi import APIRouter

from nonebot_plugin_bilichat.config import config, save_config
from nonebot_plugin_bilichat.model.config import Config
from nonebot_plugin_bilichat.request_api import init_request_apis
from nonebot_plugin_bilichat.subscribe.fetch_and_push import reset_subs_job

router = APIRouter()


@router.get("/config")
async def get_config() -> Config:
    return config


@router.post("/config")
async def set_config(data: Config) -> Config:
    global config  # noqa: PLW0603
    new_cfg = Config.model_validate(data.model_dump(exclude={"version", "webui", "nonebot", "api.local_api_config"}))
    old_cfg = config.model_copy()
    new_cfg.version = old_cfg.version
    new_cfg.nonebot = old_cfg.nonebot
    new_cfg.webui = old_cfg.webui
    new_cfg.api.local_api_config = old_cfg.api.local_api_config
    config = new_cfg

    # 重新加载一些配置
    reset_subs_job()
    init_request_apis()

    # 保存配置
    save_config()

    return config
