import asyncio
import re
import xml.etree.ElementTree as ET

import httpx
from bilireq.exceptions import GrpcError, ResponseCodeError
from bilireq.grpc.dynamic import grpc_get_user_dynamics
from bilireq.grpc.protos.bilibili.app.dynamic.v2.dynamic_pb2 import DynamicItem, DynamicType
from grpc.aio import AioRpcError
from httpx import TimeoutException
from nonebot.log import logger

from ..config import plugin_config
from ..content.dynamic import Dynamic
from ..lib.bilibili_request import get_b23_url, get_user_dynamics
from ..lib.bilibili_request.auth import AuthManager
from ..lib.content_cd import BilichatCD
from ..model.const import DYNAMIC_TYPE_IGNORE
from ..model.exception import AbortError
from ..optional import capture_exception
from .manager import Uploader


async def _handle_dynamic(up: Uploader, dyn: Dynamic):
    up.dyn_offset = max(up.dyn_offset, int(dyn.id))

    if dyn.raw_type == "web":
        up_name = dyn.raw_web["modules"]["module_author"]["name"]
        if up.nickname != up_name:
            await up.fix_nickname()

    elif dyn.raw_type == "grpc":
        assert dyn.raw_grpc and isinstance(dyn.raw_grpc, DynamicItem)
        up_name = dyn.raw_grpc.modules[0].module_author.author.name.strip()
        if up.nickname != up_name and up_name:
            await up.fix_nickname()

    type_text = f"{up.nickname} "
    if dyn.dynamic_type == DynamicType.av:
        type_text += "投稿了视频"
    elif dyn.dynamic_type == DynamicType.article:
        type_text += "投稿了专栏"
    elif dyn.dynamic_type == DynamicType.music:
        type_text += "投稿了音乐"
    elif dyn.dynamic_type == DynamicType.forward:
        type_text += "转发了一条动态"
    elif dyn.dynamic_type == DynamicType.word:
        type_text += "发布了一条文字动态"
    elif dyn.dynamic_type == DynamicType.draw:
        type_text += "发布了一条图文动态"
    else:
        type_text += "发布了一条动态"
    logger.info(f"{type_text}")

    if not dyn.url:
        dyn.url = await get_b23_url(f"https://t.bilibili.com/{dyn.id}")

    dyn_image: bytes = await dyn.get_image(plugin_config.bilichat_basic_info_style)  # type: ignore

    content = [type_text, dyn_image, dyn.url]
    for user in up.subscribed_users:
        if user.subscriptions[up.uid].dynamic:
            BilichatCD.record_cd(session_id=user.user_id, content_id=dyn.id)
            await user.push_to_user(content=content, at_all=user.subscriptions[up.uid].dynamic_at_all or user.at_all)


async def fetch_dynamics_rest(up: Uploader):
    try:
        resp: list = (await get_user_dynamics(up.uid))["items"]
    except TimeoutException:
        logger.error(f"[Dynamic] 获取 {up.nickname}({up.uid}) 超时")
        raise AbortError("Dynamic Abort")
    except ResponseCodeError as e:
        logger.error(
            f"[Dynamic] 获取 {up.nickname}({up.uid}) 失败: "
            f"[{e.code}] {e.details() if isinstance(e, AioRpcError) else e.msg}"
        )
        raise AbortError("Dynamic Abort")
    # 如果动态为空
    if not resp:
        logger.debug("未获取到任何动态")
        return
    # 如果是刚启动
    if up.dyn_offset == 0:
        up.dyn_offset = max([int(x["id_str"]) for x in resp])
        return
    dyns = [x for x in resp if int(x["id_str"]) > up.dyn_offset and x["type"] not in DYNAMIC_TYPE_IGNORE]
    dyns.reverse()
    for dyn in dyns:
        dynamic = Dynamic(id=dyn["id_str"], url="")
        await dynamic._web(raw_dyn=dyn)
        await _handle_dynamic(up, dynamic)


async def fetch_dynamics_grpc(up: Uploader):
    try:
        resp = await asyncio.wait_for(grpc_get_user_dynamics(up.uid, auth=AuthManager.get_auth()), timeout=10)
    except asyncio.TimeoutError:
        logger.error(f"[Dynamic] 获取 {up.nickname}({up.uid}) 超时")
        raise AbortError("Dynamic Abort")
    except (GrpcError, AioRpcError) as e:
        logger.error(
            f"[Dynamic] 获取 {up.nickname}({up.uid}) 失败: "
            f"[{e.code}] {e.details() if isinstance(e, AioRpcError) else e.msg}"
        )
        raise AbortError("Dynamic Abort")
    except Exception as e:
        capture_exception(e)
        raise e
    # 如果动态为空
    if not resp:
        return
    # 如果是刚启动
    if up.dyn_offset == 0:
        up.dyn_offset = max([int(x.extend.dyn_id_str) for x in resp.list])
        return
    dyns = [x for x in resp.list if int(x.extend.dyn_id_str) > up.dyn_offset and x.card_type not in DYNAMIC_TYPE_IGNORE]
    dyns.reverse()
    for dyn in dyns:
        dynamic = Dynamic(id=dyn.extend.dyn_id_str, url="")
        await dynamic._grpc(raw_dyn=dyn)
        await _handle_dynamic(up, dynamic)


async def fetch_dynamics_rss(up: Uploader) -> Dynamic | None:
    try:
        url = (
            f"{plugin_config.bilichat_rss_base}bilibili/user/dynamic/{up.uid}"
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

    except TimeoutException:
        logger.error(f"[Dynamic] 获取 {up.nickname}({up.uid}) 超时")
        raise AbortError("Dynamic Abort")
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 503:
            logger.error(f"[Dynamic] 获取 {up.nickname}({up.uid}) RSS 订阅服务不可用")
            raise AbortError("Dynamic Abort")
    except ResponseCodeError as e:
        logger.error(
            f"[Dynamic] 获取 {up.nickname}({up.uid}) 失败: "
            f"[{e.code}] {e.details() if isinstance(e, AioRpcError) else e.msg}"
        )
        raise AbortError("Dynamic Abort")
    if not items:
        logger.debug("未获取到任何动态")
        return

    all_dyn_ids = [int(re.search(r"t.bilibili.com/(\d+)", item.find("link").text).group(1)) for item in items]  # type: ignore
    # 如果是刚启动
    if up.dyn_offset == 0:
        up.dyn_offset = max(all_dyn_ids)
        return
    dyn_ids = [x for x in all_dyn_ids if x > up.dyn_offset]
    dyn_ids.reverse()
    for dyn_id in dyn_ids:
        dyn = await Dynamic.from_id(str(dyn_id))
        await _handle_dynamic(up, dyn)
