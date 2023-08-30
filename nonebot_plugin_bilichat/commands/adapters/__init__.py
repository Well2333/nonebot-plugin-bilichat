from typing import Callable, Dict

PUSH_HANDLER: Dict[str, Callable] = {}
ID_HANDLER: Dict[str, Callable] = {}

try:
    from .onebot_v11 import get_user_id, push

    PUSH_HANDLER["OneBot V11"] = push
    ID_HANDLER["OneBot V11"] = get_user_id
except Exception:
    pass

try:
    from . import onebot_v12
except Exception:
    pass

try:
    from . import mirai2
except Exception:
    pass

try:
    from . import qqguild
except Exception:
    pass
