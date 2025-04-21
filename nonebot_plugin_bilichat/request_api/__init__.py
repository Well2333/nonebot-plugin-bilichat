import random

from nonebot.log import logger
from yarl import URL

from nonebot_plugin_bilichat.config import ConfigCTX

from .base import RequestAPI

request_apis: list[RequestAPI] = []


local_api: RequestAPI | None = None
if ConfigCTX.get().api.local_api_config is not None and ConfigCTX.get().api.local_api_config.enable:
    from .local import LOCAL_REQUEST_API_PATH, LOCAL_REQUEST_API_TOKEN

    local_api = RequestAPI(URL(LOCAL_REQUEST_API_PATH), LOCAL_REQUEST_API_TOKEN, 1, "本地 API", local_api=True)


def init_request_apis():
    request_apis.clear()
    if local_api:
        request_apis.append(local_api)
        logger.info(f"本地 API 初始化成功, Token: {LOCAL_REQUEST_API_TOKEN}")
    for api in ConfigCTX.get().api.request_api:
        if api.enable:
            try:
                request_api = RequestAPI(URL(api.api), api.token, api.weight, api.note)
                request_apis.append(request_api)
                logger.info(f"API {api.api} 初始化成功, 权重: {api.weight}, 备注: {api.note}")
            except Exception as e:
                logger.exception(f"API {api.api} 初始化失败, 跳过: {e}")
        else:
            logger.warning(f"API {api.api} 未启用")
    if not request_apis:
        raise RuntimeError("未找到可用的 Bilichat API 服务, 请在配置文件中添加至少一个 API 服务或启用本地 API")
    logger.info(f"初始化 {len(request_apis)} 个 API 服务")


init_request_apis()


def get_request_api() -> RequestAPI:
    if not request_apis:
        raise RuntimeError("未找到可用的 Bilichat API 服务, 请在配置文件中添加至少一个 API 服务或启用本地 API")
    return random.choices(request_apis, weights=[api._weight for api in request_apis])[0]
