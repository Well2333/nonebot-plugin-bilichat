import asyncio
from typing import List, Union

from bilireq.exceptions import GrpcError, ResponseCodeError
from bilireq.grpc.dynamic import grpc_get_user_dynamics
from google.protobuf.json_format import MessageToDict
from grpc.aio import AioRpcError
from httpx import TimeoutException
from nonebot.exception import FinishedException
from nonebot.log import logger
from nonebot.params import CommandArg

from ..adapters.base import check_cd
from ..config import plugin_config
from ..content.dynamic import Dynamic
from ..lib.bilibili_request import get_b23_url, get_user_dynamics
from ..lib.bilibili_request.auth import gRPC_Auth
from ..lib.uid_extract import uid_extract
from ..model.exception import AbortError
from ..optional import capture_exception
from ..subscribe.dynamic import DYNAMIC_TYPE_IGNORE
from .base import bilichat

bili_check_dyn = bilichat.command("checkdynamic", aliases=set(plugin_config.bilichat_cmd_checkdynamic))


async def fetch_dynamics_rest(up_mid: int, up_name: str) -> Union[Dynamic, None]:
    try:
        resp: List = (await get_user_dynamics(up_mid))["items"]
    except TimeoutException:
        logger.error(f"[Dynamic] fetch {up_name}({up_mid}) timeout")
        raise AbortError("Dynamic Abort")
    except ResponseCodeError as e:
        logger.error(
            f"[Dynamic] fetch {up_name}({up_mid}) failed: "
            f"[{e.code}] {e.details() if isinstance(e, AioRpcError) else e.msg}"
        )
        raise AbortError("Dynamic Abort")
    # 如果动态为空
    if not resp:
        logger.debug("未获取到任何动态")
        return

    dyns = {int(x["id_str"]): x for x in resp if x["type"] not in DYNAMIC_TYPE_IGNORE}
    dyn_id = max(dyns.keys())
    dyn = dyns[dyn_id]
    check_cd(dyn["id_str"], check=False)

    url = await get_b23_url(f"https://t.bilibili.com/{dyn['id_str']}")
    dynamic = Dynamic(id=dyn["id_str"], url=url, raw=dyn, raw_type="web")
    return dynamic


async def fetch_dynamics_grpc(up_mid: int, up_name: str) -> Union[Dynamic, None]:
    try:
        resp = await asyncio.wait_for(grpc_get_user_dynamics(up_mid, auth=gRPC_Auth), timeout=10)
    except asyncio.TimeoutError:
        logger.error(f"[Dynamic] fetch {up_name}({up_mid}) timeout")
        raise AbortError("Dynamic Abort")
    except (GrpcError, AioRpcError) as e:
        logger.error(
            f"[Dynamic] fetch {up_name}({up_mid}) failed: "
            f"[{e.code}] {e.details() if isinstance(e, AioRpcError) else e.msg}"
        )
        raise AbortError("Dynamic Abort")
    except Exception as e:
        capture_exception(e)
        raise e
    # 如果动态为空
    if not resp:
        return

    dyns = {int(x.extend.dyn_id_str): x for x in resp.list if x.card_type not in DYNAMIC_TYPE_IGNORE}
    dyn_id = max(dyns.keys())
    dyn = dyns[dyn_id]
    check_cd(dyn.extend.dyn_id_str, check=False)

    url = await get_b23_url(f"https://t.bilibili.com/{dyn.extend.dyn_id_str}")
    dynamic = Dynamic(
        id=dyn.extend.dyn_id_str, url=url, dynamic_type=dyn.card_type, raw=MessageToDict(dyn), raw_type="grpc"
    )
    return dynamic


try:
    from nonebot.adapters.onebot import v11

    @bili_check_dyn.handle()
    async def check_dynamic_v11(bot: v11.Bot, uid: v11.Message = CommandArg()):
        # 获取 UP 对象
        if not uid:
            await bili_check_dyn.finish("请输入UP主的昵称呢\n`(*>﹏<*)′")
        up = await uid_extract(uid.extract_plain_text())
        if isinstance(up, str):
            await bili_check_dyn.finish(up)
            raise FinishedException

        if plugin_config.bilichat_dynamic_grpc:
            dyn = await fetch_dynamics_grpc(up.mid, up.nickname)
        else:
            dyn = await fetch_dynamics_rest(up.mid, up.nickname)

        if dyn:
            if image := await dyn.get_image(plugin_config.bilichat_dynamic_style):
                await bili_check_dyn.finish(v11.MessageSegment.image(image))

except ImportError:
    pass


try:
    import base64

    from nonebot.adapters import mirai2

    @bili_check_dyn.handle()
    async def check_dynamic_mirai(bot: mirai2.Bot, uid: mirai2.MessageChain = CommandArg()):
        # 获取 UP 对象
        if not uid:
            await bili_check_dyn.finish("请输入UP主的昵称呢\n`(*>﹏<*)′")
        up = await uid_extract(uid.extract_plain_text())
        if isinstance(up, str):
            await bili_check_dyn.finish(up)
            raise FinishedException

        if plugin_config.bilichat_dynamic_grpc:
            dyn = await fetch_dynamics_grpc(up.mid, up.nickname)
        else:
            dyn = await fetch_dynamics_rest(up.mid, up.nickname)

        if dyn:
            if image := await dyn.get_image(plugin_config.bilichat_dynamic_style):
                await bili_check_dyn.finish(mirai2.MessageSegment.image(base64=base64.b64encode(image).decode("utf-8")))

except ImportError:
    pass
