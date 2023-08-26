import asyncio

from bilireq.exceptions import GrpcError
from bilireq.grpc.dynamic import grpc_get_user_dynamics
from bilireq.grpc.protos.bilibili.app.dynamic.v2.dynamic_pb2 import (
    DynamicType,
    DynModuleType,
)
from google.protobuf.json_format import MessageToDict
from grpc.aio import AioRpcError
from loguru import logger

from ..config import plugin_config
from ..content.dynamic import Dynamic
from ..lib.bilibili_request import get_b23_url
from ..lib.bilibili_request.auth import gRPC_Auth
from ..optional import capture_exception
from .manager import SubscriptionSystem, Uploader


async def fetch_dynamics_grpc(up: Uploader):
    try:
        logger.debug(f"[Dynamic] fetch {up.nickname}({up.uid}) by gRPC")
        resp = await asyncio.wait_for(grpc_get_user_dynamics(up.uid, auth=gRPC_Auth), timeout=10)
    except asyncio.TimeoutError:
        logger.warning(f"[Dynamic] fetch {up.nickname}({up.uid}) timeout")
        return
    except (GrpcError, AioRpcError) as e:
        logger.warning(
            f"[Dynamic] fetch {up.nickname}({up.uid}) failed: "
            f"[{e.code}] {e.details() if isinstance(e, AioRpcError) else e.msg}"
        )
        return
    except Exception as e:
        capture_exception(e)
        raise e
    # 如果动态为空
    if not resp:
        return
    if up.dyn_offset == 0:
        up.dyn_offset = max([int(x.extend.dyn_id_str) for x in resp.list])
        return
    resp = [x for x in resp.list if int(x.extend.dyn_id_str) > up.dyn_offset]
    resp.reverse()
    for dyn in resp:
        # 跳过置顶动态
        if dyn.modules[0].module_author.is_top:
            continue
        up_name = dyn.modules[0].module_author.author.name
        if up.nickname != up_name:
            logger.info(f"[Dynamic] Up {up.nickname}({up.uid}) nickname changed to {up_name}")
            up.nickname = up_name

        url = ""
        type_text = f"{up.nickname} "
        if dyn.card_type == DynamicType.av:
            type_text += "投稿了视频"
            for module in dyn.modules:
                if module.module_type == DynModuleType.module_dynamic:
                    aid = module.module_dynamic.dyn_archive.avid
                    url = await get_b23_url(f"https://www.bilibili.com/video/av{aid}")
        elif dyn.card_type == DynamicType.article:
            type_text += "投稿了专栏"
            for module in dyn.modules:
                if module.module_type == DynModuleType.module_dynamic:
                    cvid = module.module_dynamic.dyn_article.id
                    url = await get_b23_url(f"https://www.bilibili.com/read/cv{cvid}")
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

        dynamic = Dynamic(
            id=dyn.extend.dyn_id_str, url=url, dynamic_type=dyn.card_type, raw=MessageToDict(dyn), raw_type="grpc"
        )

        dyn_image: bytes = await dynamic.get_image(plugin_config.bilichat_basic_info_style)  # type: ignore

        for user in up.subscribed_users:
            await user.push_dynamic(text=type_text, url=url, image=dyn_image)


async def fetch_dynamics(up: Uploader):
    try:
        return await fetch_dynamics_grpc(up)
    except Exception as e:
        logger.exception(e)


async def main():
    logger.debug("[Dynamic] Updating start")
    up_groups = SubscriptionSystem.activate_uploaders.values()

    for up in up_groups:
        await fetch_dynamics(up)

    logger.debug("[Dynamic] Updating finished")
    await asyncio.sleep(3)
