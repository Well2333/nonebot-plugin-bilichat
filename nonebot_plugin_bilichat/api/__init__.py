from fastapi import APIRouter, Depends
from fastapi.staticfiles import StaticFiles
from nonebot.log import logger

from nonebot_plugin_bilichat.config import STATIC_DIR, ConfigCTX, nonebot_config
from nonebot_plugin_bilichat.lib.auth import get_current_user

from .auth import router as auth_router
from .base import app
from .config import router as config_router

public_router = APIRouter()
public_router.include_router(auth_router)
protected_router = APIRouter()
protected_router.include_router(config_router)

# 注册路由
app.include_router(
    public_router,
    prefix=f"/{ConfigCTX.get().webui.api_path}",
)

app.include_router(
    protected_router,
    prefix=f"/{ConfigCTX.get().webui.api_path}",
    dependencies=[Depends(get_current_user)],
)
app.mount(
    f"/{ConfigCTX.get().webui.api_path}",
    StaticFiles(directory=STATIC_DIR.joinpath("html"), html=True),
    name="bilichat_webui",
)

logger.success(f"BiliChat WebUI 已启动 --> http://127.0.0.1:{nonebot_config.port}/{ConfigCTX.get().webui.api_path}")
