import random

from nonebot import get_driver
from nonebot.log import logger
from nonebot_plugin_apscheduler import scheduler
from yarl import URL

from nonebot_plugin_bilichat.config import ConfigCTX
from nonebot_plugin_bilichat.model.exception import APIError

from .base import RequestAPI

# 测试用的UID
TEST_UID = 33138220


class APIManager:
    """API管理器, 负责管理可用和不可用的API"""

    def __init__(self) -> None:
        self.apis: list[RequestAPI] = []
        self.local_api: RequestAPI | None = None

    @property
    def available_apis(self) -> list[RequestAPI]:
        return [api for api in self.apis if api.is_available]

    @property
    def unavailable_apis(self) -> list[RequestAPI]:
        return [api for api in self.apis if not api.is_available]

    def init_local_api(self) -> None:
        """初始化本地API"""
        from .local import LOCAL_REQUEST_API_PATH, LOCAL_REQUEST_API_TOKEN

        self.local_api = RequestAPI(URL(LOCAL_REQUEST_API_PATH), LOCAL_REQUEST_API_TOKEN, 1, "本地 API", local_api=True)
        self.local_api._available = True
        self.apis.append(self.local_api)
        logger.info(f"本地 API 初始化成功, Token: {LOCAL_REQUEST_API_TOKEN}")

    async def init_apis(self) -> None:
        """初始化所有API"""

        self.apis.clear()

        # 初始化本地API
        if ConfigCTX.get().api.local_api_config is not None and ConfigCTX.get().api.local_api_config.enable:
            self.init_local_api()

        # 初始化远程API
        for api in ConfigCTX.get().api.request_api:
            if api.enable:
                request_api = RequestAPI(URL(api.api), api.token, api.weight, api.note)
                self.apis.append(request_api)
                logger.info(f"API {api.api} 已初始化, 权重: {api.weight}, 备注: {api.note}")
            else:
                logger.warning(f"API {api.api} 未启用")

        await self.check_unavailable_apis()

        if scheduler.get_job("bilichat_api_health_check"):
            scheduler.remove_job("bilichat_api_health_check")

        scheduler.add_job(
            self.check_unavailable_apis,
            "interval",
            id="bilichat_api_health_check",
            seconds=ConfigCTX.get().api.api_health_check_interval,
            jitter=15,
            max_instances=1,
        )

    def get_api(self) -> RequestAPI:
        """获取一个可用的API实例

        Returns:
            RequestAPI: API实例

        Raises:
            RuntimeError: 没有可用的API时抛出
        """
        if not self.available_apis:
            raise APIError("没有可用的 API 服务")
        # 使用权重进行随机选择
        return random.choices(self.available_apis, weights=[api._weight for api in self.available_apis])[0]

    async def check_unavailable_apis(self) -> None:
        """检查不可用API的可用性"""
        if not self.unavailable_apis:
            return

        logger.debug(f"开始检查 {len(self.unavailable_apis)} 个不可用API")
        apis_to_check = self.unavailable_apis.copy()

        for api in apis_to_check:
            try:
                await api.check_api_availability()
            except APIError as e:
                logger.debug(f"API {api.base_url} 检查失败: {e}")
                continue

        logger.debug(
            f"检查 {len(apis_to_check)} 个API完成, \
            可用 {len(self.available_apis)} 个, \
            不可用 {len(self.unavailable_apis)} 个\n"
            + "\n".join([f"{'⭕️' if api.is_available else '❌'} {api.base_url}" for api in self.apis])
        )


# 创建全局API管理器实例
api_manager = APIManager()


# 初始化API
@get_driver().on_startup
async def init_apis():
    await api_manager.init_apis()


def get_request_api() -> RequestAPI:
    """获取一个可用的API实例"""
    return api_manager.get_api()
