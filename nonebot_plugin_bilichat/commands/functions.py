from nonebot.adapters import Message
from nonebot.params import CommandArg
from nonebot_plugin_saa import Image, MessageFactory

from ..config import plugin_config
from ..lib.fetch_dynamic import fetch_last_dynamic
from ..lib.uid_extract import uid_extract
from .base import bilichat

bili_check_dyn = bilichat.command("checkdynamic", aliases=set(plugin_config.bilichat_cmd_checkdynamic))


@bili_check_dyn.handle()
async def check_dynamic_v11(uid: Message = CommandArg()):
    # 获取 UP 对象
    if not uid:
        await bili_check_dyn.finish("请输入UP主的昵称呢\n`(*>﹏<*)′")
    up = await uid_extract(uid.extract_plain_text())
    if isinstance(up, str):
        await bili_check_dyn.finish(up)
    if dyn := await fetch_last_dynamic(up):
        if image := await dyn.get_image(plugin_config.bilichat_dynamic_style):
            await MessageFactory(Image(image)).send()
