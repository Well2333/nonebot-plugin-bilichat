from typing import Union

from pydantic import BaseModel, Extra, Field

from .bilibili_request import search_user


class SearchUp(BaseModel, extra=Extra.ignore):
    nickname: str = Field(alias="title")
    mid: int

    def __str__(self) -> str:
        return f"{self.nickname}({self.mid})"


class SearchResult(BaseModel, extra=Extra.ignore):
    items: list[SearchUp] = []


async def uid_extract(text: str) -> Union[str, SearchUp]:
    text_u = text.strip(""""'“”‘’""").strip()
    resp = await search_user(text_u)
    result = SearchResult(**resp)
    if result.items:
        for up in result.items:
            if up.nickname == text_u:
                return up
        return "未找到该 UP，你可能在找：\n" + "\n".join([str(up) for up in result.items])
    return "未找到该 UP 主呢\n`(*>﹏<*)′"
