from ..lib.store import cache_dir
from pydantic import BaseModel
from typing import Dict, Optional, Union, List


class Episode(BaseModel):
    title: Optional[str]
    content: List[str]
    jieba: Optional[Dict]
    openai: Optional[str]


class Cache(BaseModel):
    id: str
    title: str
    episodes: Dict[str, Episode]

    @classmethod
    def create(cls, id: str, title: str, episodes: Dict[str, Episode]):
        cache = cls(id=id, title=title, episodes=episodes)
        cache.save()
        return cache

    @classmethod
    def get(cls, id: Union[str, int]):
        f = cache_dir.joinpath(f"{id}.json")
        return cls.parse_file(f,encoding="utf-8") if f.exists() else None

    def save(self):
        cache_dir.touch(0o755)
        f = cache_dir.joinpath(f"{self.id}.json")
        f.write_text(self.json(ensure_ascii=False),encoding="utf-8")
