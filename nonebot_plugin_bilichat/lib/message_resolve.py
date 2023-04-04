import re

from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Image, Voice, FlashImage

from .b23_extract import b23_extract


async def message_resolve(message: MessageChain):
    if message.only(Image) or message.has(Voice) or message.has(FlashImage):
        return

    message_str = message.as_persistent_string(binary=False, exclude=[Image])
    p = re.compile(r"av(\d{1,16})|BV(1[A-Za-z0-9]{2}4.1.7[A-Za-z0-9]{2})|cv(\d{1,16})")
    if not p.search(message_str) and ("b23.tv" in message_str or "b23.wtf" in message_str):
        message_str = await b23_extract(message_str) or message_str
    if bili_number := p.search(message_str):
        bili_number = bili_number[0]
        return bili_number
    else:
        return
