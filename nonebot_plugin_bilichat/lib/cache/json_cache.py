import json

from anyio import Path
from nonebot.compat import PYDANTIC_V2
from nonebot.log import logger

from ..store import cache_dir
from .cache import BaseCache


class JSONFileCache(BaseCache):
    async def save(self) -> None:
        file_path = cache_dir.joinpath(f"{self.id}.json")
        logger.debug(f"保存 {self.id} 的缓存到 {file_path.absolute().as_posix()}")
        if PYDANTIC_V2:
            await Path(file_path).write_text(self.model_dump_json(), encoding="utf-8")  # type: ignore
        else:
            await Path(file_path).write_text(self.json(ensure_ascii=False), encoding="utf-8")  # type: ignore

    @classmethod
    async def load(cls, id: str, **kwargs) -> "JSONFileCache":
        file_path = cache_dir.joinpath(f"{id}.json")
        return cls(**json.loads(file_path.read_bytes())) if file_path.exists() else cls(id=id, **kwargs)
