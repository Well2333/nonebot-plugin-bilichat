from fastapi.staticfiles import StaticFiles
from nonebot.log import logger

from ..config import plugin_config, raw_config
from ..lib.strings import generate_framed_text

if plugin_config.bilichat_webui_path:
    from . import bilibili_auth, subs_config  # noqa: F401
    from .base import app
    from .webui import webui_dir

    if webui_dir.joinpath("index.html").exists():
        app.mount("/", StaticFiles(directory=webui_dir, html=True), name="webui")

    propmt = [
        "Setting Up BILICHAT WebUI at",
        f"http://{raw_config.host}:{raw_config.port}/{plugin_config.bilichat_webui_path}/",
        "You can upgrade WebUI manualy at",
        f"http://{raw_config.host}:{raw_config.port}/{plugin_config.bilichat_webui_path}/webui",
    ]
    if plugin_config.bilichat_webui_path == "bilichat":
        propmt.extend(
            [
                "WARNING: Bilichat WebUI is currently running on default path. "
                "Please consider to use different path via adding config `bilichat_webui_path` in .env file.",
            ]
        )
    logger.success("\n" + generate_framed_text(propmt))
