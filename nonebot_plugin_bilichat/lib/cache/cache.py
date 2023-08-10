from typing import Dict, List, Optional

from nonebot.log import logger
from pydantic import BaseModel


class BaseCache(BaseModel):
    id: str
    title: Optional[str] = None
    content: Optional[List[str]] = None
    jieba: Optional[Dict] = None
    openai: Optional[str] = None
    newbing: Optional[str] = None

    async def save(self, *args, **kwargs):
        logger.debug(f"saving cache of {self.id} to memory")
        return
