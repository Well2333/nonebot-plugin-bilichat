from typing import Dict, Literal

from bilireq.exceptions import GrpcError, ResponseCodeError
from bilireq.grpc.dynamic import grpc_get_dynamic_detail
from bilireq.grpc.protos.bilibili.app.dynamic.v2.dynamic_pb2 import DynamicType, DynModuleType
from google.protobuf.json_format import MessageToDict
from nonebot.log import logger
from pydantic import BaseModel

from ..lib.bilibili_request import get_b23_url, get_dynamic
from ..lib.bilibili_request.auth import gRPC_Auth
from ..lib.draw.dynamic import draw_dynamic
from ..model.exception import AbortError
from ..optional import capture_exception


class Dynamic(BaseModel):
    id: str
    """动态编号"""
    url: str
    """b23 链接"""
    dynamic_type: DynamicType.ValueType = DynamicType.dyn_none
    "动态类型"
    raw: Dict = {}
    """动态的原始信息"""
    raw_type: Literal["web", "grpc", None] = None
    
    @property
    def bili_id(self) -> str:
        return f"动态id: {self.id}"

    async def _grpc(self):
        logger.debug("正在使用 gRPC 获取动态信息")
        _dyn = await grpc_get_dynamic_detail(dynamic_id=self.id, auth=gRPC_Auth)
        dyn = _dyn.item
        self.raw = MessageToDict(dyn)
        self.raw_type = "grpc"
        self.dynamic_type = dyn.card_type
        if dyn.card_type == DynamicType.av:
            for module in dyn.modules:
                if module.module_type == DynModuleType.module_dynamic:
                    aid = module.module_dynamic.dyn_archive.avid
                    self.url = await get_b23_url(f"https://www.bilibili.com/video/av{aid}")
        elif dyn.card_type == DynamicType.article:
            for module in dyn.modules:
                if module.module_type == DynModuleType.module_dynamic:
                    cvid = module.module_dynamic.dyn_article.id
                    self.url = await get_b23_url(f"https://www.bilibili.com/read/cv{cvid}")

    async def _web(self):
        logger.debug("正在使用 RestAPI 获取动态信息")
        dyn = (await get_dynamic(self.id))["item"]
        self.raw = dyn
        self.raw_type = "web"

        if dyn["type"] == "DYNAMIC_TYPE_AV":
            self.dynamic_type = DynamicType.av
            aid = dyn["modules"]["module_dynamic"]["major"]["archive"]["aid"]
            self.url = await get_b23_url(f"https://www.bilibili.com/video/av{aid}")
        elif dyn["type"] == "DYNAMIC_TYPE_ARTICLE":
            self.dynamic_type = DynamicType.article
            cvid = dyn["modules"]["module_dynamic"]["major"]["article"]["id"]
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
                if dynamic.raw:  # 如果存在动态内容，则很可能是数据结构变化了
                    logger.debug(dynamic.raw)
                    capture_exception(extra={"dynamic_data": dynamic.raw})
            # web
            try:
                await dynamic._web()
            except Exception as e:
                if isinstance(e, ResponseCodeError):
                    logger.warning(f"无法使用 RestAPI 获取动态信息: {e}")
                else:
                    logger.exception(e)
                    if dynamic.raw:  # 如果存在动态内容，则很可能是数据结构变化了
                        logger.debug(dynamic.raw)
                        capture_exception(extra={"dynamic_data": dynamic.raw})
                raise AbortError("动态查询信息异常，请查看控制台获取更多信息")

        if not dynamic.url:
            dynamic.url = await get_b23_url(f"https://t.bilibili.com/{bili_number}")
        return dynamic

    async def get_image(self, style: str):
        return await draw_dynamic(dynid=self.id, raw=self.raw, raw_type=self.raw_type)
