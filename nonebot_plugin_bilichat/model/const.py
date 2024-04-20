from bilireq.grpc.protos.bilibili.app.dynamic.v2.dynamic_pb2 import DynamicType


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
DYNAMIC_TYPE_MAP = {
    "DYNAMIC_TYPE_FORWARD": DynamicType.forward,
    "DYNAMIC_TYPE_WORD": DynamicType.word,
    "DYNAMIC_TYPE_DRAW": DynamicType.draw,
    "DYNAMIC_TYPE_AV": DynamicType.av,
    "DYNAMIC_TYPE_ARTICLE": DynamicType.article,
    "DYNAMIC_TYPE_MUSIC": DynamicType.music,
}