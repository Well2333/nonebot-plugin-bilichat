import re

from nonebot.adapters import Message
from nonebot.exception import FinishedException
from nonebot.log import logger
from nonebot.params import CommandArg
from nonebot.typing import T_State
from nonebot_plugin_alconna.uniseg import Hyper, Image, MsgTarget, Reply, Text, UniMessage, UniMsg

from ..base_content_parsing import check_cd
from ..config import plugin_config
from ..content import Column, Dynamic, Video
from ..lib.b23_extract import b23_extract
from ..lib.fetch_dynamic import fetch_last_dynamic
from ..lib.uid_extract import uid_extract
from ..model.exception import AbortError
from .base import bilichat

bili_check_dyn = bilichat.command("checkdynamic", aliases=set(plugin_config.bilichat_cmd_checkdynamic))


@bili_check_dyn.handle()
async def check_dynamic_v11(target: MsgTarget, uid: Message = CommandArg()):
    # 获取 UP 对象
    if not uid:
        await bili_check_dyn.finish("请输入UP主的昵称呢\n`(*>﹏<*)′")
    up = await uid_extract(uid.extract_plain_text())
    if isinstance(up, str):
        await bili_check_dyn.finish(up)
    if dyn := await fetch_last_dynamic(up):
        if image := await dyn.get_image(plugin_config.bilichat_dynamic_style):
            await UniMessage(Image(raw=image)).send(target=target)


bili_fetch_content = bilichat.command("fetch", aliases=set(plugin_config.bilichat_cmd_fetch), block=True)


@bili_fetch_content.handle()
async def fetch_check(state: T_State, msg: UniMsg, target: MsgTarget):
    _msgs = msg.copy()
    if Reply in msg:
        # 如果是回复消息
        # 1. 如果是自身消息且允许自身消息
        # 2. 如果被回复消息中包含对自身的at
        # 满足上述任一条件，则将被回复的消息的内容添加到待解析的内容中
        _msgs.append(Text(str(msg[Reply, 0].msg)))

    bililink = None
    for _msg in _msgs[Text] + _msgs[Hyper]:
        # b23 格式的链接
        _msg_str = _msg.__repr__()
        if "b23" in _msg_str:
            if b23 := re.search(r"b23.(tv|wtf)[\\/]+(\w+)", _msg_str):  # type: ignore
                bililink = await b23_extract(list(b23.groups()))
                break
        # av bv cv 格式和动态的链接
        for seg in ("av", "bv", "cv", "dynamic", "opus", "t.bilibili.com"):
            if seg in _msg_str.lower():
                bililink = _msg_str
                break

    if not bililink:
        raise FinishedException

    content: Dynamic | None = None

    try:
        if matched := re.search(r"(dynamic|opus|t.bilibili.com)/(\d{1,128})", bililink):
            _id = matched.group()
            logger.info(f"dynamic id: {_id}")
            content = await Dynamic.from_id(_id)
        else:
            raise AbortError("该功能目前仅可用于图文动态哦~")

        if content:
            check_cd(f"{target.id}_-_{content.id}", check=False)
            state["_content_"] = content
        else:
            raise AbortError(f"查询 {bililink} 返回内容为空")
    except AbortError as e:
        logger.info(e)
        await bili_fetch_content.finish(e.message)
    except FinishedException:
        raise FinishedException


@bili_fetch_content.handle()
async def fetch_content(target: MsgTarget, state: T_State):
    content: Video | Dynamic = state["_content_"]
    if isinstance(content, Video):
        raise FinishedException
    elif isinstance(content, Dynamic):
        logger.info("尝试下载动态图片")
        try:
            if imgs := await content.fetch_content():
                await UniMessage([Image(raw=img) for img in imgs]).send(target=target)
                raise FinishedException
            else:
                await bili_fetch_content.finish("动态无可获取的图片哦~")
        except Exception as e:
            if isinstance(e, FinishedException):
                raise
            logger.exception(e)
            await bili_fetch_content.finish(f"动态图片获取失败 {type(e)}: {e}")
