from beanie import Document
from pydantic import Field

from .cache import BaseCache


class MongoCache(Document,BaseCache):
    id: str = Field(default_factory=str, alias="_id")

    class Settings:
        name = "nonebot_plugin_bilichat.cache"

    @classmethod
    async def load(cls, id: str, **kwargs) -> "MongoCache":
        if cache := await cls.get(id):
            return cache
        if cache := await cls.insert_one(MongoCache(_id=id)):
            return cache
        raise RuntimeError(f"Unable to insert cache {cache}")
