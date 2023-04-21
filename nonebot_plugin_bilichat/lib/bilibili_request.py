from typing import Union

import httpx
from bilireq.grpc.dynamic import grpc_get_followed_dynamics
from bilireq.grpc.protos.bilibili.app.dynamic.v2.dynamic_pb2 import (
    DynamicType,
    DynDetailsReply,
    DynDetailsReq,
)
from bilireq.grpc.protos.bilibili.app.dynamic.v2.dynamic_pb2_grpc import DynamicStub
from bilireq.grpc.protos.bilibili.app.playurl.v1.playurl_pb2 import (
    PlayViewReply,
    PlayViewReq,
)
from bilireq.grpc.protos.bilibili.app.playurl.v1.playurl_pb2_grpc import PlayURLStub
from bilireq.grpc.protos.bilibili.app.view.v1.view_pb2 import ViewReply, ViewReq
from bilireq.grpc.protos.bilibili.app.view.v1.view_pb2_grpc import ViewStub
from bilireq.grpc.protos.bilibili.community.service.dm.v1.dm_pb2 import (
    DmViewReply,
    DmViewReq,
)
from bilireq.grpc.protos.bilibili.community.service.dm.v1.dm_pb2_grpc import DMStub
from bilireq.grpc.utils import grpc_request
from bilireq.utils import get, post
from loguru import logger

from bilireq.auth import Auth

hc = httpx.AsyncClient(
    headers={
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36 Edg/112.0.1722.39"
        )
    }
)
Bili_Auth = Auth()


async def relation_modify(uid: Union[str, int], act: int):
    """
    修改关系

    Args:
        uid: 用户ID
        act: 操作
    Act:
        1:	 关注
        2:	 取关
        3:	 悄悄关注
        4:	 取消悄悄关注
        5:	 拉黑
        6:	 取消拉黑
        7:	 踢出粉丝团
    """
    url = "https://api.bilibili.com/x/relation/modify"
    data = {
        "act": act,
        "fid": int(uid),
    }
    return await post(url, params=data, auth=Bili_Auth, raw=True)


async def dynamic_like(dynid):
    """
    动态点赞

    Args:
        dynid: 动态ID
    """
    url = "https://api.vc.bilibili.com/dynamic_like/v1/dynamic_like/thumb"
    data = {"dynamic_id": str(dynid), "up": 1}
    return await post(url, data=data, auth=Bili_Auth)


async def get_b23_url(burl: str) -> str:
    """
    b23 链接转换

    Args:
        burl: 需要转换的 BiliBili 链接
    """
    url = "https://api.bilibili.com/x/share/click"
    data = {
        "build": 6700300,
        "buvid": 0,
        "oid": burl,
        "platform": "android",
        "share_channel": "COPY",
        "share_id": "public.webview.0.0.pv",
        "share_mode": 3,
    }
    resp = await post(url, data=data)
    logger.debug(resp)
    return resp["content"]


async def search_user(keyword: str):
    """
    搜索用户
    """
    url = "https://api.bilibili.com/x/web-interface/search/type"
    data = {"keyword": keyword, "search_type": "bili_user"}
    resp = (await hc.get(url, params=data)).json()
    logger.debug(resp)
    return resp["data"]


async def get_user_space_info(uid: int):
    """
    获取用户空间信息
    """
    url = "https://app.bilibili.com/x/v2/space"
    params = {
        "vmid": uid,
        "build": 6840300,
        "ps": 1,
    }
    return await get(url, params=params)


async def get_player(aid: int, cid: int):
    """
    获取视频播放器信息
    """
    url = "https://api.bilibili.com/x/player/v2"
    params = {
        "aid": aid,
        "cid": cid,
    }
    return await get(url, params=params, auth=Bili_Auth)


async def grpc_get_followed_dynamics_noads():
    resp = await grpc_get_followed_dynamics(auth=Bili_Auth)
    exclude_list = [
        DynamicType.ad,
        DynamicType.live,
        DynamicType.live_rcmd,
        DynamicType.banner,
    ]
    dynamic_list = [dyn for dyn in resp.dynamic_list.list if dyn.card_type not in exclude_list]
    dynamic_list.reverse()
    return dynamic_list


@grpc_request
async def grpc_get_dynamic_details(dynamic_ids: str, **kwargs) -> DynDetailsReply:
    stub = DynamicStub(kwargs.pop("_channel"))
    req = DynDetailsReq(dynamic_ids=dynamic_ids)
    return await stub.DynDetails(req, **kwargs)


@grpc_request
async def grpc_get_view_info(aid: int = 0, bvid: str = "", **kwargs) -> ViewReply:
    stub = ViewStub(kwargs.pop("_channel"))
    if aid:
        req = ViewReq(aid=aid)
    elif bvid:
        req = ViewReq(bvid=bvid)
    else:
        raise ValueError("aid or bvid must be provided")
    return await stub.View(req, **kwargs)


@grpc_request
async def grpc_get_dmview(pid: int, oid: int, type: int = 1, **kwargs) -> DmViewReply:
    stub = DMStub(kwargs.pop("_channel"))
    req = DmViewReq(pid=pid, oid=oid, type=type)
    return await stub.DmView(req, **kwargs)


@grpc_request
async def grpc_get_playview(aid: int, cid: int, **kwargs) -> PlayViewReply:
    stub = PlayURLStub(kwargs.pop("_channel"))
    req = PlayViewReq(aid=aid, cid=cid, qn=128, fnval=464)
    return await stub.PlayView(req, **kwargs)
