from importlib.metadata import version

import nonebot
from fastapi import FastAPI
from nonebot.drivers import ReverseDriver
from nonebot.drivers.fastapi import Driver as FastAPIDriver
from nonebot.log import logger
from packaging.version import Version

from nonebot_plugin_bilichat.config import DATA_DIR, __version__, nonebot_config
from nonebot_plugin_bilichat.config import config as bilichat_config

from .base import MINIMUM_API_VERSION

LOCAL_REQUEST_API_PATH = ""
LOCAL_REQUEST_API_TOKEN = ""

if bilichat_config.api.local_api_config is not None and bilichat_config.api.local_api_config.enable:
    try:
        from bilichat_request.config import BILICHAT_MIN_VERSION, set_config
        from bilichat_request.config import config as bilichat_request_config
    except ImportError as e:
        raise ImportError("bilichat-request 未安装, 请先安装 bilichat-request") from e

    bilichat_request_config = bilichat_request_config.model_validate(
        bilichat_config.api.local_api_config.model_dump(exclude={"enable"})
    )
    bilichat_request_config.data_path = DATA_DIR.joinpath("bilichat_request").as_posix()

    set_config(bilichat_request_config)

    logger.info(f"本地 API 配置: {bilichat_request_config}")

    # 版本检查

    if Version(version("bilichat-request")) < MINIMUM_API_VERSION:
        raise RuntimeError(
            f"bilichat-request 版本过低, 当前: {version('bilichat-request')} 最低: {MINIMUM_API_VERSION}"
        )

    if Version(BILICHAT_MIN_VERSION) > Version(__version__):
        raise RuntimeError(
            f"bilichat-request 需求更高版本 nonebot-plugin-bilichat 当前: {__version__} 最低: {BILICHAT_MIN_VERSION}"
        )

    from bilichat_request.api.base import app

    driver: FastAPIDriver = nonebot.get_driver()  # type: ignore

    if not isinstance(driver, ReverseDriver) or not isinstance(driver.server_app, FastAPI):
        raise NotImplementedError("Only FastAPI reverse driver is supported.")

    driver.server_app.mount("/", app, name="bilichat_api")

    LOCAL_REQUEST_API_PATH = f"http://127.0.0.1:{nonebot_config.port}/{bilichat_request_config.api_path}"
    LOCAL_REQUEST_API_TOKEN = bilichat_request_config.api_access_token
