import asyncio
from asyncio import Lock

from nonebot.exception import FinishedException
from nonebot.log import logger
from nonebot.plugin import CommandGroup
from nonebot.rule import to_me
from nonebot_plugin_alconna.uniseg import MsgTarget, Text, UniMessage
from nonebot_plugin_uninfo import Uninfo

from nonebot_plugin_bilichat.config import ConfigCTX
from nonebot_plugin_bilichat.model.exception import APIError
from nonebot_plugin_bilichat.model.subscribe import UserInfo
from nonebot_plugin_bilichat.request_api import RequestAPI, get_request_api
from nonebot_plugin_bilichat.subscribe.status import SubsStatus

bilichat = CommandGroup(
    ConfigCTX.get().nonebot.cmd_start,
    rule=to_me() if ConfigCTX.get().nonebot.command_to_me else None,
    block=ConfigCTX.get().nonebot.block,
)


async def check_lock() -> Lock:
    while SubsStatus.modify_lock.locked():
        await asyncio.sleep(0)
    return SubsStatus.modify_lock


async def get_user(session: Uninfo) -> UserInfo:
    user = ConfigCTX.get().subs.users_dict.get(
        f"{session.scope}_type{session.scene.type}_{session.scene.id}",
        UserInfo(info=session, subscribes={}),
    )
    logger.info(f"get user: {user.id}")
    return user


async def get_api(target: MsgTarget) -> RequestAPI:
    try:
        return get_request_api()
    except APIError:
        await UniMessage(Text("无API可用, 请检查API配置")).send(
            target=target, fallback=ConfigCTX.get().nonebot.fallback
        )
        raise FinishedException from None
