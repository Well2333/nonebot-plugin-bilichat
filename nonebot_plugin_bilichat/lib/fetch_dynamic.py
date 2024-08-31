import asyncio
import re
import xml.etree.ElementTree as ET

import httpx
from bilireq.exceptions import GrpcError, ResponseCodeError
from bilireq.grpc.dynamic import grpc_get_user_dynamics
from grpc.aio import AioRpcError
from httpx import TimeoutException
from nonebot.log import logger

from ..config import plugin_config
from ..content.dynamic import Dynamic
from ..lib.bilibili_request import get_b23_url, get_user_dynamics
from ..lib.bilibili_request.auth import AuthManager
from ..lib.uid_extract import SearchUp
from ..model.const import DYNAMIC_TYPE_IGNORE
from ..model.exception import AbortError
from ..optional import capture_exception
from ..subscribe.manager import SubscriptionSystem


async def fetch_last_dynamic(up: SearchUp) -> Dynamic | None:
    if SubscriptionSystem.config.dynamic_method == "grpc":
        try:
            return await _fetchlast_grpc(up.mid, up.nickname)
        except AbortError:
            return await _fetchlast_rest(up.mid, up.nickname)
    elif SubscriptionSystem.config.dynamic_method == "rest":
        return await _fetchlast_rest(up.mid, up.nickname)
    elif SubscriptionSystem.config.dynamic_method == "rss":
        return await _fetchlast_rss(up.mid)


async def _fetchlast_rest(up_mid: int, up_name: str) -> Dynamic | None:
    try:
        resp: list = (await get_user_dynamics(up_mid))["items"]
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

    url = await get_b23_url(f"https://t.bilibili.com/{dyn['id_str']}")
    dynamic = Dynamic(id=dyn["id_str"], url=url, raw_web=dyn, raw_type="web")
    return dynamic


async def _fetchlast_grpc(up_mid: int, up_name: str) -> Dynamic | None:
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

    url = await get_b23_url(f"https://t.bilibili.com/{dyn.extend.dyn_id_str}")
    dynamic = Dynamic(id=dyn.extend.dyn_id_str, url=url, dynamic_type=dyn.card_type, raw_grpc=dyn, raw_type="grpc")
    return dynamic


async def _fetchlast_rss(mid: int) -> Dynamic | None:
    try:
        url = (
            f"{plugin_config.bilichat_rss_base}bilibili/user/dynamic/{mid}"
            + f"?key={plugin_config.bilichat_rss_key}"
            if plugin_config.bilichat_rss_key
            else ""
        )
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            response.raise_for_status()
            rss_xml = response.text
        root = ET.fromstring(rss_xml)
        items = root.findall("channel/item")

        for item in items:
            link: str = item.find("link").text  # type: ignore
            dynamic_id: str = re.search(r"t.bilibili.com/(\d+)", link).group(1)  # type: ignore
            return await Dynamic.from_id(dynamic_id)
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 503:
            logger.error(f"RSS 订阅服务不可用 {type(e)}:{e}")
            raise AbortError("Dynamic Abort")
        else:
            logger.exception(f"获取 {mid} RSS 动态失败: {e}")
            return
    except Exception as e:
        logger.exception(f"[Dynamic] 获取 {mid} RSS 动态失败: {e}")
        return
