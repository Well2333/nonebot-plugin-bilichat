from nonebot.adapters.onebot.v11 import Bot as V11_Bot
from nonebot.adapters.onebot.v11 import MessageEvent as V11_ME
from nonebot.adapters.onebot.v11 import MessageSegment as V11_MS
from nonebot.adapters.onebot.v12 import Bot as V12_Bot
from nonebot.adapters.onebot.v12 import MessageEvent as V12_ME
from nonebot.adapters.onebot.v12 import MessageSegment as V12_MS

from typing import Union
from random import randint


async def get_image(data: bytes, bot: Union[V11_Bot, V12_Bot]):
    if isinstance(bot, V11_Bot):
        return V11_MS.image(data)
    elif isinstance(bot, V12_Bot):
        fileid = await bot.upload_file(type="data", name=f"{randint(0, 999999):06d}.jpg", data=data)
        return V12_MS.image(file_id=fileid["file_id"])


async def get_reply(event: Union[V11_ME, V12_ME], id_: Union[str, int] = 0):
    message_id: str = str(id_ or event.message_id)
    if isinstance(event, V11_ME):
        return V11_MS.reply(int(message_id))
    elif isinstance(event, V12_ME):
        return V12_MS.reply(message_id=message_id, user_id=event.get_user_id())
