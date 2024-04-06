import asyncio
from typing import List, Union

from bilireq.exceptions import GrpcError, ResponseCodeError
from bilireq.grpc.dynamic import grpc_get_user_dynamics
from bilireq.grpc.protos.bilibili.app.dynamic.v2.dynamic_pb2 import (
    DynamicType,
)
from google.protobuf.json_format import MessageToDict
from grpc.aio import AioRpcError
from httpx import TimeoutException
from nonebot.log import logger

from ..base_content_parsing import check_cd
from ..content.dynamic import Dynamic
from ..lib.bilibili_request import get_b23_url, get_user_dynamics
from ..lib.bilibili_request.auth import AuthManager
from ..lib.uid_extract import SearchUp
from ..model.exception import AbortError
from ..optional import capture_exception
from ..subscribe.manager import SubscriptionSystem

DYNAMIC_TYPE_MAP = {
    "DYNAMIC_TYPE_FORWARD": DynamicType.forward,
    "DYNAMIC_TYPE_WORD": DynamicType.word,
    "DYNAMIC_TYPE_DRAW": DynamicType.draw,
    "DYNAMIC_TYPE_AV": DynamicType.av,
    "DYNAMIC_TYPE_ARTICLE": DynamicType.article,
    "DYNAMIC_TYPE_MUSIC": DynamicType.music,
}

DYNAMIC_TYPE_IGNORE = {
    "DYNAMIC_TYPE_AD",
    "DYNAMIC_TYPE_LIVE",
    "DYNAMIC_TYPE_LIVE_RCMD",
    "DYNAMIC_TYPE_BANNER",
    DynamicType.ad,
    DynamicType.live,
    DynamicType.live_rcmd,
    DynamicType.banner,
}


async def fetch_last_dynamic(up: SearchUp) -> Union[Dynamic, None]:
    if SubscriptionSystem.config.dynamic_grpc:
        try:
            return await _fetch_grpc(up.mid, up.nickname)
        except AbortError:
            return await _fetch_rest(up.mid, up.nickname)
    else:
        return await _fetch_rest(up.mid, up.nickname)


async def _fetch_rest(up_mid: int, up_name: str) -> Union[Dynamic, None]:
    try:
        resp: List = (await get_user_dynamics(up_mid))["items"]
    except TimeoutException:
        logger.error(f"[Dynamic] 获取 {up_name}({up_mid}) 超时")
        raise AbortError("Dynamic Abort")
    except ResponseCodeError as e:
        logger.error(
            f"[Dynamic] 获取 {up_name}({up_mid}) 失败: "
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


async def _fetch_grpc(up_mid: int, up_name: str) -> Union[Dynamic, None]:
    try:
        resp = await asyncio.wait_for(grpc_get_user_dynamics(up_mid, auth=AuthManager.get_auth()), timeout=10)
    except asyncio.TimeoutError:
        logger.error(f"[Dynamic] 获取 {up_name}({up_mid}) 超时")
        raise AbortError("Dynamic Abort")
    except (GrpcError, AioRpcError) as e:
        logger.error(
            f"[Dynamic] 获取 {up_name}({up_mid}) 失败: "
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
