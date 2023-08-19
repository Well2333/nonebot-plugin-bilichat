from pydantic import BaseModel

from ..lib.bilibili_request import get_b23_url
from ..lib.draw.dynamic import draw_dynamic


class Dynamic(BaseModel):
    id: str
    """动态编号"""
    uploader: str = ""
    """UP主"""
    url: str
    """b23 链接"""

    @classmethod
    async def from_id(cls, bili_number: str):
        if not bili_number.isdigit():
            bili_number = bili_number.lstrip("qwertyuiopasdfghjklzxcvbnm/.")
        return cls(id=bili_number, url=await get_b23_url(f"https://www.bilibili.com/dynamic/{bili_number}"))

    async def get_image(self, style: str):
        return await draw_dynamic(self.id)
