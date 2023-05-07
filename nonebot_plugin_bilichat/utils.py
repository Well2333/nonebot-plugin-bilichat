from os import PathLike
from random import randint
from typing import Union

from anyio import open_file
from nonebot.adapters import MessageSegment
from nonebot.adapters.onebot.v11 import Bot as V11_Bot
from nonebot.adapters.onebot.v11 import GroupMessageEvent as V11_GME
from nonebot.adapters.onebot.v11 import MessageEvent as V11_ME
from nonebot.adapters.onebot.v11 import MessageSegment as V11_MS
from nonebot.adapters.onebot.v11 import NoticeEvent as V11_NE
from nonebot.adapters.onebot.v11 import PrivateMessageEvent as V11_PME
from nonebot.adapters.onebot.v12 import Bot as V12_Bot
from nonebot.adapters.onebot.v12 import GroupMessageEvent as V12_GME
from nonebot.adapters.onebot.v12 import MessageEvent as V12_ME
from nonebot.adapters.onebot.v12 import MessageSegment as V12_MS
from nonebot.adapters.onebot.v12 import NoticeEvent as V12_NE
from nonebot.adapters.onebot.v12 import PrivateMessageEvent as V12_PME

BOT = Union[V11_Bot, V12_Bot]
MESSAGE_EVENT = Union[V11_ME, V12_ME]
GROUP_MESSAGE_EVENT = Union[V11_GME, V12_GME]
PRIVATE_MESSAGE_EVENT = Union[V11_PME, V12_PME]
NOTICE_EVENT = Union[V11_NE, V12_NE]


async def get_image(image: Union[bytes, "PathLike[str]", str], bot: BOT) -> MessageSegment:
    if isinstance(image, bytes):
        return await get_image_from_bytes(image, bot)
    elif isinstance(image, PathLike):
        async with await open_file(image, "rb") as f:
            content = await f.read()
        return await get_image_from_bytes(content, bot)
    else:
        raise NotImplementedError


async def get_image_from_bytes(image: bytes, bot: BOT) -> MessageSegment:
    if isinstance(bot, V11_Bot):
        return V11_MS.image(image)
    elif isinstance(bot, V12_Bot):
        fileid = await bot.upload_file(type="data", name=f"{randint(0, 999999):06d}.jpg", data=image)
        return V12_MS.image(file_id=fileid["file_id"])
    else:
        raise NotImplementedError


async def get_reply(event: MESSAGE_EVENT, id_: Union[str, int] = 0) -> MessageSegment:
    if isinstance(event, V11_ME):
        return V11_MS.reply(int(id_ or event.message_id))
    elif isinstance(event, V12_ME):
        return V12_MS.reply(message_id=str(id_ or event.message_id), user_id=event.get_user_id())
    else:
        raise NotImplementedError
