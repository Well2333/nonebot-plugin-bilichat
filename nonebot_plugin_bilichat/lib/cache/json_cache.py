from anyio import Path
from nonebot.log import logger

from ..store import cache_dir
from .cache import BaseCache


class JSONFileCache(BaseCache):
    async def save(self) -> None:
        file_path = cache_dir.joinpath(f"{self.id}.json")
        logger.debug(f"saving cache of {self.id} to {file_path.absolute().as_posix()}")
        await Path(file_path).write_text(self.json(ensure_ascii=False), encoding="utf-8")

    @classmethod
    async def load(cls, id: str, **kwargs) -> "JSONFileCache":
        file_path = cache_dir.joinpath(f"{id}.json")
        return cls.parse_file(file_path) if file_path.exists() else cls(id=id, **kwargs)
