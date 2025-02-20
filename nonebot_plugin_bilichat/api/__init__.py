from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi.staticfiles import StaticFiles
from nonebot.log import logger

from nonebot_plugin_bilichat.config import STATIC_DIR, ConfigCTX, nonebot_config

from .base import app
from .config import router as config_router

security = HTTPBearer()
router = APIRouter()
router.include_router(config_router)


async def verify_token(cred: HTTPAuthorizationCredentials = Depends(security)):
    if cred.credentials != ConfigCTX.get().webui.api_access_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing token",
        )


app.include_router(
    router,
    prefix=f"/{ConfigCTX.get().webui.api_path}",
    dependencies=[Depends(verify_token)] if ConfigCTX.get().webui.api_access_token else [],
)
app.mount(
    f"/{ConfigCTX.get().webui.api_path}",
    StaticFiles(directory=STATIC_DIR.joinpath("html"), html=True),
    name="bilichat_webui",
)

logger.success(f"BiliChat WebUI 已启动 --> http://127.0.0.1:{nonebot_config.port}/{ConfigCTX.get().webui.api_path}")
