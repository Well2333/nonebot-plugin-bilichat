import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import List, Union

from nonebot.log import logger
from pydantic import BaseModel, Field

from .bilibili_request import search_user


class SearchUp(BaseModel):
    nickname: str = Field(alias="title")
    mid: int

    def __str__(self) -> str:
        return f"{self.nickname}({self.mid})"


class SearchResult(BaseModel):
    items: List[SearchUp] = []


async def search(text_u: str) -> Union[str, SearchUp]:
    resp = await search_user(text_u)
    result = SearchResult(**resp)
    if result.items:
        for up in result.items:
            if up.nickname == text_u or str(up.mid) in text_u:
                logger.debug(up)
                return up
        return "未找到该 UP，你可能在找：\n" + "\n".join([str(up) for up in result.items])
    return "未找到该 UP 主呢\n`(*>﹏<*)′"


async def uid_extract(text: str) -> Union[str, SearchUp]:
    text_u = text.strip(""""'“”‘’""").strip().replace("：", ":")
    up = await search(text_u)
    if isinstance(up, str) and text_u.isdigit():
        up = await search("UID: " + text_u)
    return up


def run_async_in_thread(func, *args):
    # 在新线程中运行异步函数
    async def thread_func():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return await func(*args)
        finally:
            loop.close()  # 关闭事件循环

    with ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(asyncio.run, thread_func())
        return future.result()


def uid_extract_sync(text: str) -> Union[str, SearchUp]:
    # 调用 run_async_in_thread 来运行异步函数并获取结果
    return run_async_in_thread(uid_extract, text)
