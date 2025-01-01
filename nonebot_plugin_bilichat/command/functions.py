from nonebot.adapters import Message
from nonebot.log import logger
from nonebot.params import CommandArg
from nonebot.typing import T_State
from nonebot_plugin_alconna.uniseg import Image, MsgTarget, UniMessage, UniMsg

from nonebot_plugin_bilichat.config import config
from nonebot_plugin_bilichat.lib.content_cd import BilichatCD
from nonebot_plugin_bilichat.request_api import get_request_api

from .base import bilichat

bili_check_dyn = bilichat.command("checkdynamic", aliases=set(config.nonebot.cmd_checkdynamic))


@bili_check_dyn.handle()
async def check_dynamic_v11(target: MsgTarget, uid: Message = CommandArg()):
    # 获取 UP 对象
    if not uid:
        await bili_check_dyn.finish("请输入UP主的昵称或uid")
    api = get_request_api()
    up = await api.tools_search_up(uid.extract_plain_text())
    if not up:
        await bili_check_dyn.finish(f"未找到 UP {uid.extract_plain_text()}")
    elif isinstance(up, list):
        upstr = "\n".join([str(u) for u in up])
        await bili_check_dyn.finish(f"未找到 UP {uid.extract_plain_text()}, 猜你想找: \n{upstr}")
    if dyns := await api.subs_dynamic(up.uid):
        latest_dyn = max(dyns, key=lambda x: x.dyn_id)
        BilichatCD.record_cd(session_id=target.id, content_id=str(latest_dyn.dyn_id))
        if dyn := await api.content_dynamic(latest_dyn.dyn_id, config.api.browser_shot_quality):
            await UniMessage(Image(raw=dyn.img_bytes)).send(target=target)


bili_fetch_content = bilichat.command("fetch", aliases=set(config.nonebot.cmd_fetch), block=True)


@bili_fetch_content.handle()
async def fetch_check(state: T_State, msg: UniMsg, target: MsgTarget):
    await bili_fetch_content.finish("WIP")


logger.success("Loaded: nonebot_plugin_bilichat.command.functions")