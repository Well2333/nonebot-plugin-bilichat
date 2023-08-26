from typing import Callable, Dict

from nonebot.log import logger

PUSH_HANDLER: Dict[str, Callable] = {}
ID_HANDLER: Dict[str, Callable] = {}

try:
    from .onebot_v11 import get_user_id, push

    PUSH_HANDLER["OneBot V11"] = push
    ID_HANDLER["OneBot V11"] = get_user_id
    logger.success("OneBot V11 adapter was loaded successfully")
except Exception:
    pass

try:
    from . import onebot_v12

    logger.success("OneBot V12 adapter was loaded successfully")
except Exception:
    pass

try:
    from . import mirai2

    logger.success("mirai2 adapter was loaded successfully")
except Exception:
    pass

try:
    from . import qqguild

    logger.success("QQ Guild adapter was loaded successfully")
except Exception:
    pass
