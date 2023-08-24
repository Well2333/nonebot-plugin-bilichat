from typing import Dict, Literal, Optional

from bilireq.exceptions import GrpcError, ResponseCodeError
from bilireq.grpc.dynamic import grpc_get_dynamic_detail
from google.protobuf.json_format import MessageToDict
from nonebot.log import logger
from pydantic import BaseModel

from ..auth import gRPC_Auth
from ..lib.bilibili_request import get_b23_url, get_dynamic
from ..lib.draw.dynamic import draw_dynamic
from ..model.exception import AbortError
from ..optional import capture_exception


class Dynamic(BaseModel):
    id: str
    """动态编号"""
    url: str
    """b23 链接"""
    raw: Dict = {}
    """动态的原始信息"""
    raw_type: Literal["web", "grpc", None] = None

    async def _grpc(self):
        logger.debug("正在使用 gRPC 获取动态信息")
        _dyn = await grpc_get_dynamic_detail(dynamic_id=self.id, auth=gRPC_Auth)
        dyn = MessageToDict(_dyn.item)
        self.raw = dyn
        self.raw_type = "grpc"
        # 获取动态内容信息
        # with open("test.json", "w", encoding="utf-8") as f:
        #     # json.dump(dyn.item.__dict__, f, ensure_ascii=False, indent=4)
        #     f.write(json.dumps(dyn, ensure_ascii=False))
        # 如果是内容类型的
        if dyn["cardType"] == "av":
            for module in dyn["modules"]:
                if module["moduleType"] == "module_dynamic":
                    aid = module["moduleDynamic"]["dynArchive"]["avid"]
                    self.url = await get_b23_url(f"https://www.bilibili.com/video/av{aid}")
        elif dyn["cardType"] == "article":
            for module in dyn["modules"]:
                if module["moduleType"] == "module_dynamic":
                    cvid = module["moduleDynamic"]["dynArticle"]["id"]
                    self.url = await get_b23_url(f"https://www.bilibili.com/read/cv{cvid}")

    async def _web(self):
        logger.debug("正在使用 RestAPI 获取动态信息")
        dyn = (await get_dynamic(self.id))["item"]
        self.raw = dyn
        self.raw_type = "web"

        if dyn["type"] == "DYNAMIC_TYPE_AV":
            aid = dyn["modules"]["module_dynamic"]["major"]["archive"]["aid"]
            self.url = await get_b23_url(f"https://www.bilibili.com/video/av{aid}")
        elif dyn["type"] == "DYNAMIC_TYPE_ARTICLE":
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
        return await draw_dynamic(self.id, raw=self.raw, raw_type=self.raw_type)
