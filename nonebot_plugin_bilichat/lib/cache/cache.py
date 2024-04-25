from nonebot.log import logger
from pydantic import BaseModel


class BaseCache(BaseModel):
    id: str
    title: str | None = None
    content: list[str] | None = None
    jieba: dict | None = None
    openai: str | None = None
    newbing: str | None = None

    async def save(self, *args, **kwargs):
        logger.debug(f"保存 {self.id} 的缓存到内存")
