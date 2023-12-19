import asyncio
import threading
from queue import Queue
from typing import List, Union

from nonebot.log import logger
from pydantic import BaseModel, Extra, Field

from .bilibili_request import search_user


class SearchUp(BaseModel, extra=Extra.ignore):
    nickname: str = Field(alias="title")
    mid: int

    def __str__(self) -> str:
        return f"{self.nickname}({self.mid})"


class SearchResult(BaseModel, extra=Extra.ignore):
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


def uid_extract_sync(text: str) -> Union[str, SearchUp]:
    # 创建一个队列用于从线程中获取结果
    queue = Queue()

    # 定义一个运行异步函数并将结果放入队列的函数
    def run_and_store_result():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(uid_extract(text))
        queue.put(result)
        loop.close()

    # 创建并启动线程
    thread = threading.Thread(target=run_and_store_result)
    thread.start()
    thread.join()

    # 从队列中获取返回结果
    return queue.get()