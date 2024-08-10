from typing import Any, Literal

from bilireq.exceptions import GrpcError, ResponseCodeError
from bilireq.grpc.dynamic import grpc_get_dynamic_detail
from bilireq.grpc.protos.bilibili.app.dynamic.v2.dynamic_pb2 import DynamicItem, DynamicType, DynModuleType
from google.protobuf.json_format import MessageToDict
from httpx import TimeoutException
from nonebot.log import logger
from pydantic import BaseModel

from ..config import plugin_config
from ..lib.bilibili_request import get_b23_url, get_dynamic, hc
from ..lib.bilibili_request.auth import AuthManager
from ..lib.draw.dynamic import draw_dynamic
from ..model.const import DYNAMIC_TYPE_MAP
from ..model.exception import AbortError
from ..optional import capture_exception


class Dynamic(BaseModel):
    id: str
    """动态编号"""
    url: str
    """b23 链接"""
    dynamic_type: DynamicType.ValueType = DynamicType.dyn_none
    "动态类型"
    raw_type: Literal["web", "grpc", None] = None
    """动态的原始信息"""
    raw_grpc: Any | None = None  # DynamicItem
    raw_web: dict = {}

    @property
    def bili_id(self) -> str:
        return f"动态id: {self.id}"

    async def _grpc(self, raw_dyn: DynamicItem | None = None):
        if not raw_dyn:
            logger.debug("正在使用 gRPC 获取动态信息")
            for i in range(plugin_config.bilichat_neterror_retry):
                try:
                    raw_dyn = (await grpc_get_dynamic_detail(dynamic_id=self.id, auth=AuthManager.get_auth())).item
                    break
                except TimeoutException:
                    logger.warning(f"请求超时，重试第 {i + 1}/{plugin_config.bilichat_neterror_retry} 次")
            else:
                raise AbortError("请求超时")
        else:
            logger.debug("使用已有的 gRPC 动态信息")
        self.raw_grpc = raw_dyn
        self.raw_type = "grpc"
        self.dynamic_type = raw_dyn.card_type
        if raw_dyn.card_type == DynamicType.av:
            for module in raw_dyn.modules:
                if module.module_type == DynModuleType.module_dynamic:
                    aid = module.module_dynamic.dyn_archive.avid
                    self.url = await get_b23_url(f"https://www.bilibili.com/video/av{aid}")
        elif raw_dyn.card_type == DynamicType.article:
            for module in raw_dyn.modules:
                if module.module_type == DynModuleType.module_dynamic:
                    cvid = module.module_dynamic.dyn_article.id
                    self.url = await get_b23_url(f"https://www.bilibili.com/read/cv{cvid}")

    async def _web(self, raw_dyn: dict | None = None):
        if not raw_dyn:
            logger.debug("正在使用 RestAPI 获取动态信息")
            for i in range(plugin_config.bilichat_neterror_retry):
                try:
                    raw_dyn = (await get_dynamic(self.id))["item"]
                    break
                except TimeoutException:
                    logger.warning(f"请求超时，重试第 {i + 1}/{plugin_config.bilichat_neterror_retry} 次")
            else:
                raise AbortError("请求超时")
        else:
            logger.debug("使用已有的 RestAPI 动态信息")
        assert raw_dyn
        self.raw_web = raw_dyn
        self.raw_type = "web"

        self.dynamic_type = DYNAMIC_TYPE_MAP.get(raw_dyn["type"], DynamicType.dyn_none)

        if self.dynamic_type == DynamicType.av:
            aid = raw_dyn["modules"]["module_dynamic"]["major"]["archive"]["aid"]
            self.url = await get_b23_url(f"https://www.bilibili.com/video/av{aid}")
        elif self.dynamic_type == DynamicType.article:
            cvid = raw_dyn["modules"]["module_dynamic"]["major"]["article"]["id"]
            self.url = await get_b23_url(f"https://www.bilibili.com/read/cv{cvid}")

    @classmethod
    async def from_id(cls, bili_number: str):
        if not bili_number.isdigit():
            bili_number = bili_number.lstrip("qwertyuiopasdfghjklzxcvbnm/.")

        dynamic = cls(id=bili_number, url="")

        try:
            await dynamic._grpc()
        except Exception as e:
            if isinstance(e, GrpcError):
                logger.warning(f"无法使用 gRPC 获取动态信息: {e}")
            else:
                logger.exception(e)
                if dynamic.raw_grpc:  # 如果存在动态内容，则很可能是数据结构变化了
                    grpc_content = MessageToDict(dynamic.raw_grpc)
                    logger.debug(grpc_content)
                    capture_exception(extra={"dynamic_data": grpc_content})
            # web
            try:
                await dynamic._web()
            except Exception as e:
                if isinstance(e, ResponseCodeError):
                    logger.warning(f"无法使用 RestAPI 获取动态信息: {e}")
                else:
                    logger.exception(e)
                    if dynamic.raw_web:  # 如果存在动态内容，则很可能是数据结构变化了
                        logger.debug(dynamic.raw_web)
                        capture_exception(extra={"dynamic_data": dynamic.raw_web})
                raise AbortError("动态查询信息异常，请查看控制台获取更多信息")

        if not dynamic.url:
            dynamic.url = await get_b23_url(f"https://t.bilibili.com/{bili_number}")
        # with open("dynamic.json", "w", encoding="utf-8") as f:
        #     import json
        #     json.dump(dynamic.dict(), f, ensure_ascii=False)
        return dynamic

    async def get_image(self, style: str):
        raw = self.raw_web if self.raw_type == "web" else MessageToDict(self.raw_grpc)  # type: ignore
        return await draw_dynamic(dynid=self.id, raw=raw, raw_type=self.raw_type)

    async def fetch_content(self) -> list[bytes] | list[None]:
        items = []
        result = []

        def search(element):
            if isinstance(element, dict):
                for key, value in element.items():
                    if key in ("dynDraw", "draw") and isinstance(value, dict):
                        i = value.get("items")
                        if i and isinstance(i, list):
                            items.extend(i)
                    search(value)
            elif isinstance(element, list):
                for item in element:
                    search(item)

        search(self.raw_web if self.raw_type == "web" else MessageToDict(self.raw_grpc))  # type: ignore
        if items:
            for c, item in enumerate(items):
                logger.debug(f"获取图片({c}/{len(items)})：{item['src']}")
                for i in range(plugin_config.bilichat_neterror_retry):
                    try:
                        resq = await hc.get(item["src"])
                        result.append(resq.content)
                        break
                    except TimeoutException:
                        logger.warning(f"请求超时，重试第 {i + 1}/{plugin_config.bilichat_neterror_retry} 次")
                else:
                    logger.error(f"无法获取图片，请求超时 {plugin_config.bilichat_neterror_retry} 次：{item['src']}")
        else:
            logger.debug(f"动态 {self.dynamic_type} 没用可下载的内容")
        return result
