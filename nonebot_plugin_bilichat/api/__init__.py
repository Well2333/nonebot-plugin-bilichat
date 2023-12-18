from nonebot.log import logger

from ..config import plugin_config, raw_config
from ..lib.strings import generate_framed_text

if plugin_config.bilichat_api_path:
    from . import base, bilibili_auth, subs_config  # noqa: F401

    propmt = [
        "SETTING UP BILICHAT API AT",
        f"http://{raw_config.host}:{raw_config.port}/{plugin_config.bilichat_api_path}/api/",
    ]
    if plugin_config.bilichat_api_path == "bilichat":
        propmt.extend(
            [
                "WARNING: Bilichat API is currently running on default path. "
                "Please consider to use different path via adding config `bilichat_api_path` in .env file.",
            ]
        )
    logger.success("\n" + generate_framed_text(propmt))
