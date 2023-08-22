import json
from typing import Dict, Optional

from bilireq.grpc.dynamic import grpc_get_dynamic_detail
from google.protobuf.json_format import MessageToDict
from nonebot.log import logger
from pydantic import BaseModel

from ..auth import gRPC_Auth
from ..lib.bilibili_request import get_b23_url
from ..lib.draw.dynamic import draw_dynamic
from ..optional import capture_exception


class Dynamic(BaseModel):
    id: str
    """动态编号"""
    dyn_type: str = ""
    """动态类型"""
    url: str
    """b23 链接"""
    raw: Optional[Dict] = None
    """动态的原始信息"""

    @classmethod
    async def from_id(cls, bili_number: str):
        if not bili_number.isdigit():
            bili_number = bili_number.lstrip("qwertyuiopasdfghjklzxcvbnm/.")

        url = ""
        dyn = None
        try:
            logger.debug("正在使用 gRPC 获取动态信息")
            _dyn = await grpc_get_dynamic_detail(dynamic_id=bili_number, auth=gRPC_Auth)
            dyn = MessageToDict(_dyn.item)

            # 获取动态内容信息
            # with open("test.json", "w", encoding="utf-8") as f:
            #     # json.dump(dyn.item.__dict__, f, ensure_ascii=False, indent=4)
            #     f.write(json.dumps(dyn, ensure_ascii=False))

            # 如果是内容类型的
            if dyn["cardType"] == "av":
                for module in dyn["modules"]:
                    if module["moduleType"] == "module_dynamic":
                        aid = module["moduleDynamic"]["dynArchive"]["avid"]
                        url = await get_b23_url(f"https://www.bilibili.com/video/av{aid}")
            elif dyn["cardType"] == "article":
                for module in dyn["modules"]:
                    if module["moduleType"] == "module_dynamic":
                        cvid = module["moduleDynamic"]["dynArticle"]["id"]
                        url = await get_b23_url(f"https://www.bilibili.com/read/cv{cvid}")
        except Exception as e:
            if dyn:  # 如果存在动态内容，则很可能是数据结构变化了
                capture_exception(extra={"dynamic_data": dyn})
            logger.exception(e)

        if not url:
            url = await get_b23_url(f"https://t.bilibili.com/{bili_number}")

        return cls(id=bili_number, url=url, raw=dyn)

    async def get_image(self, style: str):
        return await draw_dynamic(self.id, raw=self.raw)
