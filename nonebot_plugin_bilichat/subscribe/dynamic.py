import asyncio
from typing import List

from bilireq.exceptions import GrpcError, ResponseCodeError
from bilireq.grpc.dynamic import grpc_get_user_dynamics
from bilireq.grpc.protos.bilibili.app.dynamic.v2.dynamic_pb2 import (
    DynamicType,
    DynModuleType,
)
from google.protobuf.json_format import MessageToDict
from grpc.aio import AioRpcError
from httpx import TimeoutException
from nonebot.log import logger

from ..base_content_parsing import check_cd
from ..config import plugin_config
from ..content.dynamic import Dynamic
from ..lib.bilibili_request import get_b23_url, get_user_dynamics
from ..lib.bilibili_request.auth import AuthManager
from ..lib.fetch_dynamic import DYNAMIC_TYPE_IGNORE, DYNAMIC_TYPE_MAP
from ..model.exception import AbortError
from ..optional import capture_exception
from .manager import Uploader


async def fetch_dynamics_rest(up: Uploader):
    try:
        resp: List = (await get_user_dynamics(up.uid))["items"]
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
        check_cd(dyn["id_str"], check=False)
        up.dyn_offset = max(up.dyn_offset, int(dyn["id_str"]))
        up_name = dyn["modules"]["module_author"]["name"]
        if up.nickname != up_name:
            logger.info(f"[Dynamic] Up {up.nickname}({up.uid}) 更改昵称为 {up_name}")
            up.nickname = up_name

        url = ""
        type_text = f"{up.nickname} "
        dyn_type = DYNAMIC_TYPE_MAP.get(dyn["type"], DynamicType.dyn_none)
        if dyn_type == DynamicType.av:
            type_text += "投稿了视频"
            aid = dyn["modules"]["module_dynamic"]["major"]["archive"]["aid"]
            url = await get_b23_url(f"https://www.bilibili.com/video/av{aid}")
            check_cd(aid, check=False)
        elif dyn_type == DynamicType.article:
            type_text += "投稿了专栏"
            cvid = dyn["modules"]["module_dynamic"]["major"]["article"]["id"]
            url = await get_b23_url(f"https://www.bilibili.com/read/cv{cvid}")
            check_cd(cvid, check=False)
        elif dyn_type == DynamicType.music:
            type_text += "投稿了音乐"
        elif dyn_type == DynamicType.forward:
            type_text += "转发了一条动态"
        elif dyn_type == DynamicType.word:
            type_text += "发布了一条文字动态"
        elif dyn_type == DynamicType.draw:
            type_text += "发布了一条图文动态"
        else:
            type_text += "发布了一条动态"

        if not url:
            url = await get_b23_url(f"https://t.bilibili.com/{dyn['id_str']}")

        logger.info(f"{type_text}")

        dynamic = Dynamic(id=dyn["id_str"], url=url, dynamic_type=dyn_type, raw=dyn, raw_type="web")
        dyn_image: bytes = await dynamic.get_image(plugin_config.bilichat_basic_info_style)  # type: ignore

        content = [type_text, dyn_image, url]
        for user in up.subscribed_users:
            if user.subscriptions[up.uid].dynamic:
                await user.push_to_user(
                    content=content, at_all=user.subscriptions[up.uid].dynamic_at_all or user.at_all
                )


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
        check_cd(dyn.extend.dyn_id_str, check=False)
        up.dyn_offset = max(up.dyn_offset, int(dyn.extend.dyn_id_str))
        up_name = dyn.modules[0].module_author.author.name
        if up.nickname != up_name:
            logger.info(f"[Dynamic] Up {up.nickname}({up.uid}) 更改昵称为 {up_name}")
            up.nickname = up_name

        url = ""
        type_text = f"{up.nickname} "
        if dyn.card_type == DynamicType.av:
            type_text += "投稿了视频"
            for module in dyn.modules:
                if module.module_type == DynModuleType.module_dynamic:
                    aid = module.module_dynamic.dyn_archive.avid
                    url = await get_b23_url(f"https://www.bilibili.com/video/av{aid}")
                    check_cd(aid, check=False)
        elif dyn.card_type == DynamicType.article:
            type_text += "投稿了专栏"
            for module in dyn.modules:
                if module.module_type == DynModuleType.module_dynamic:
                    cvid = module.module_dynamic.dyn_article.id
                    url = await get_b23_url(f"https://www.bilibili.com/read/cv{cvid}")
                    check_cd(cvid, check=False)
        elif dyn.card_type == DynamicType.music:
            type_text += "投稿了音乐"
        elif dyn.card_type == DynamicType.forward:
            type_text += "转发了一条动态"
        elif dyn.card_type == DynamicType.word:
            type_text += "发布了一条文字动态"
        elif dyn.card_type == DynamicType.draw:
            type_text += "发布了一条图文动态"
        else:
            type_text += "发布了一条动态"

        if not url:
            url = await get_b23_url(f"https://t.bilibili.com/{dyn.extend.dyn_id_str}")

        logger.info(f"{type_text}")

        dynamic = Dynamic(
            id=dyn.extend.dyn_id_str, url=url, dynamic_type=dyn.card_type, raw=MessageToDict(dyn), raw_type="grpc"
        )

        dyn_image: bytes = await dynamic.get_image(plugin_config.bilichat_basic_info_style)  # type: ignore

        content = [type_text, dyn_image, url]
        for user in up.subscribed_users:
            if user.subscriptions[up.uid].dynamic:
                await user.push_to_user(
                    content=content, at_all=user.subscriptions[up.uid].dynamic_at_all or user.at_all
                )
