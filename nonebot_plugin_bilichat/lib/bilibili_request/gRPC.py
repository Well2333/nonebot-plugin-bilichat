from bilireq.grpc.protos.bilibili.app.playurl.v1.playurl_pb2 import PlayViewReply, PlayViewReq
from bilireq.grpc.protos.bilibili.app.playurl.v1.playurl_pb2_grpc import PlayURLStub
from bilireq.grpc.protos.bilibili.app.view.v1.view_pb2 import ViewReply, ViewReq
from bilireq.grpc.protos.bilibili.app.view.v1.view_pb2_grpc import ViewStub
from bilireq.grpc.utils import grpc_request


@grpc_request
async def grpc_get_playview(aid: int, cid: int, **kwargs) -> PlayViewReply:
    stub = PlayURLStub(kwargs.pop("_channel"))
    req = PlayViewReq(aid=aid, cid=cid, qn=128, fnval=464)
    return await stub.PlayView(req, **kwargs)

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