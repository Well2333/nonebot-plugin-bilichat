import random

from nonebot.log import logger
from yarl import URL

from nonebot_plugin_bilichat.config import config

from .base import RequestAPI

request_apis: list[RequestAPI] = []
for api in config.api.request_api:
    try:
        request_api = RequestAPI(URL(api.api), api.token, api.weight, api.note)
        request_apis.append(request_api)
        logger.info(f"API {api.api} 初始化成功, 权重: {api.weight}, 备注: {api.note}")
    except Exception as e:  # noqa: PERF203
        logger.exception(f"API {api.api} 初始化失败, 跳过: {e}")

if config.api.local_api_config is not None and config.api.local_api_config.enable:
    from .local import LOCAL_REQUEST_API_PATH, LOCAL_REQUEST_API_TOKEN

    request_apis.append(
        RequestAPI(URL(LOCAL_REQUEST_API_PATH), LOCAL_REQUEST_API_TOKEN, 0, "本地 API", skip_version_checking=True)
    )


def get_request_api() -> RequestAPI:
    if not request_apis:
        raise RuntimeError("未找到可用的 Bilichat API 服务, 请添加至少一个 API 服务")
    return random.choice(request_apis)
